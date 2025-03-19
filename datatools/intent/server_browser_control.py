#!/usr/bin/python3
"""
HTTP server to control the browser.
"""

import json
import socketserver
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from typing import Tuple

from datatools.intent.targets import browse


class Server(BaseHTTPRequestHandler):

    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer) -> None:
        super().__init__(request, client_address, server)

    def log_message(self, fmt, *args):
        return

    def respond_with_path(self, status, path):
        self.respond(status, 'text/plain', (path + '\n').encode('utf-8'))

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        content_type = self.headers.get('Content-Type')
        mime_type = content_type.split(';')[0]

        match mime_type:
            case 'text/uri-list':
                browse(post_body.decode('utf-8'))

        self.respond(200, 'application/json', json.dumps({}).encode('utf-8'))

    def respond(self, status, content_type, content):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(content)


httpd = HTTPServer(("0.0.0.0", 7777), Server)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
