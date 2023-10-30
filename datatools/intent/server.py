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

from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        for k, v in self.headers.items():
            print(k, v)
        self.respond(200, 'application/json', b'{}')

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        self.respond(200, 'application/json', post_body)

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
