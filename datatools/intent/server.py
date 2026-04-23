#!/usr/bin/python3
"""
Intents HTTP server.
Decouples intents, triggered in datatools apps, from their effects.

HTTP server accepts entity as the body of HTTP POST request,
and reacts, depending on Content-Type
"""

import json
import os
import socketserver
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from typing import *

from datatools.intent import SERVER_PORT
from datatools.intent.handler_send_entity import default_folder, handler_send_entity
from datatools.intent.post_request_router import route_post_request
from datatools.intent.response import Response
from datatools.intent.target_folder import set_target_folder
from datatools.intent.targets import get_target_folder


class Server(BaseHTTPRequestHandler):

    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer) -> None:
        super().__init__(request, client_address, server)

    def log_message(self, fmt, *args):
        return

    def respond_with(self, response: Response):
        self.send_response(response.status)
        self.send_header('Content-Type', response.content_type)
        self.end_headers()
        self.wfile.write(response.content)

    def respond_with_path(self, status, path):
        self.respond_with(Response(status, 'text/plain', (path + '\n').encode('utf-8')))

    def do_DELETE(self):
        set_target_folder(default_folder())
        handler_send_entity.folder = get_target_folder()
        self.respond_with_path(200, get_target_folder())

    def do_GET(self):
        if self.path == '/':
            self.respond_with_path(200, get_target_folder())
        elif self.path == '/favicon.ico':
            self.respond_with_path(404, '')
        elif self.path == '/homepage':
            with open(os.environ['WORK_PATH'] + '/homepage.html', 'rb') as file:
                self.respond_with(Response(200, 'text/html', file.read()))
        else:
            match self.path.split('.')[-1]:
                case 'txt':
                    mime_type = 'text/plain; charset=utf-8'
                case 'html':
                    mime_type = 'text/html; charset=utf-8'
                case 'svg':
                    mime_type = 'image/svg+xml; charset=utf-8'
                case 'json':
                    mime_type = 'application/json; charset=utf-8'
                case _:
                    mime_type = 'application/octet-stream'

            path = get_target_folder() + self.path
            print('Reading file ' + path)

            with open(path, 'rb') as file:
                data = file.read()

            print('Read file ' + path + ", size " + str(len(data)))
            self.respond_with(Response(200, mime_type, data))

    def do_PUT(self):
        content_len = int(self.headers.get('Content-Length'))
        path = self.rfile.read(content_len).decode('utf-8')

        if os.path.exists(path):
            set_target_folder(path)
            handler_send_entity.folder = path
            self.respond_with_path(200, path)
        else:
            self.respond_with_path(404, path)

    def do_POST(self):
        print('Handling POST')
        headers = self.headers

        print(str(headers))
        content_len = int(headers.get('Content-Length'))

        post_body = self.rfile.read(content_len)

        route_post_request(headers, post_body)

        print('Handling POST; responding')
        self.respond_with(Response(200, 'application/json', json.dumps({}).encode('utf-8')))
        print('Handling POST; responded')


if __name__ == '__main__':
    httpd = HTTPServer(("0.0.0.0", SERVER_PORT), Server)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
