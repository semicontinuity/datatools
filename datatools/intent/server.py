#!/usr/bin/python3
"""
Intents HTTP server.
Decouples intents, triggered in datatools apps, from their effects.

HTTP server accepts entity as the body of HTTP POST request,
and passes it to STDIN of launched "y explore" command.
Environment variables for the launched process are specified in "x-env" HTTP header
as JSON with the format {"var":"value"..}.
For working directory of the process, the value of the variable PWD is used.
"""
import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from typing import Dict, List


def exe(cwd: str, args: List[str], env: Dict[str, str], stdin: bytes = None):
    env = os.environ | env
    proc = subprocess.Popen(
        args,
        cwd=cwd,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    out, err = proc.communicate(stdin)
    if proc.returncode != 0:
        raise Exception(proc.returncode)
    return out.decode()


class Server(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        self.respond(200, 'application/json', b'{}')

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        payload = json.loads(post_body)

        env_str = self.headers['x-env']
        if env_str is None:
            self.respond(400, 'application/json', b'{"error":"x-env header missing"}')
            return

        env = json.loads(env_str)
        cwd = env['CWD']
        if cwd is None:
            self.respond(400, 'application/json', b'{"error":"CWD variable in x-env header missing"}')
            return

        del env['CWD']

        if 'PWD' in env:
            del env['PWD']

        out = exe(
            cwd,
            ['y', 'explore'],
            {},
            post_body
        )
        print(out)
        self.respond(200, 'application/json', json.dumps({}).encode('utf-8'))

    def respond(self, status, content_type, content):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(content)


httpd = HTTPServer(("localhost", 8888), Server)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
