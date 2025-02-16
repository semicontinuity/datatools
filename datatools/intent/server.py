#!/usr/bin/python3
"""
Intents HTTP server.
Decouples intents, triggered in datatools apps, from their effects.

HTTP server accepts entity as the body of HTTP POST request,
and reacts, depending on Content-Type
"""

import json
import os
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from datatools.jt2h.app import page_node_basic_auto
from datatools.jt2h.app_json_page import page_node
from datatools.util.subprocess import exe


class Server(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        self.respond(200, 'application/json', b'{}')

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)

        match self.headers.get('Content-Type'):
            case 'text/uri-list':
                self.browse(post_body)
            case 'application/sql':
                self.browse(
                    self.write_temp_file(post_body, '.sql')
                )
            case 'application/json-lines':
                lines = self.json_lines(post_body)
                html = str(page_node_basic_auto(lines))
                self.browse(
                    self.write_temp_file(
                        html.encode('utf-8'),
                        '.html'
                    )
                )
            case 'application/json':
                data = json.loads(post_body.decode('utf-8'))
                html = str(page_node(data))
                self.browse_new_tab(
                    self.write_temp_file(
                        html.encode('utf-8'),
                        '.html'
                    )
                )

        self.respond(200, 'application/json', json.dumps({}).encode('utf-8'))

    def json_lines(self, data):
        decode = data.decode('utf-8')
        split = decode.split('\n')
        return [json.loads(s) for s in split if s]

    def write_temp_file(self, contents, suffix):
        import tempfile
        import os
        fd, path = tempfile.mkstemp(suffix=suffix, prefix="temp", dir=os.environ['HOME'] + '/boards', text=True)
        with os.fdopen(fd, 'w+b') as tmp:
            tmp.write(contents)
        return path

    def browse_new_tab(self, url):
        exe(
            os.environ['HOME'],
            ['firefox', url],
            {},
        )

    def browse(self, url):
        if type(url) is str:
            url = url.encode('utf-8')
        exe(
            os.environ['HOME'],
            ['browse_url'],
            {},
            url
        )

    def respond(self, status, content_type, content):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(content)


httpd = HTTPServer(("localhost", 7777), Server)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
