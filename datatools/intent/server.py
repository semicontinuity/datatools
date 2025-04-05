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
from socket import socket
from typing import Tuple

from datatools.intent import SERVER_PORT
from datatools.intent.handler_json_lines import handle_json_lines
from datatools.intent.handler_multipart import handle_multipart
from datatools.intent.handler_send_entity import default_folder, handler_send_entity
from datatools.intent.target_folder import set_target_folder, get_target_folder
from datatools.intent.targets import to_clipboard, write_temp_file, browse_new_tab, open_in_idea, html_to_browser
from datatools.json.json2html import to_blocks_html
from datatools.jt2h.app_json_page import page_node, md_node
from datatools.jt2h.json_node_delegate_json import JsonNodeDelegateJson
from datatools.tui.popup_selector import choose


class Server(BaseHTTPRequestHandler):

    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer) -> None:
        super().__init__(request, client_address, server)

    def log_message(self, fmt, *args):
        return

    def respond_with_path(self, status, path):
        self.respond(status, 'text/plain', (path + '\n').encode('utf-8'))

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
                self.respond(200, 'text/html', file.read())
        else:
            match self.path.split('.')[-1]:
                case 'txt':
                    mime_type = 'text/plain'
                case 'html':
                    mime_type = 'text/html'
                case 'svg':
                    mime_type = 'image/svg+xml'
                case 'json':
                    mime_type = 'application/json'
                case _:
                    mime_type = 'application/octet-stream'

            with open(get_target_folder() + self.path, 'rb') as file:
                self.respond(200, mime_type, file.read())

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
        the_title = self.headers.get('X-Title')
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        content_type = self.headers.get('Content-Type')
        mime_type = content_type.split(';')[0]

        match mime_type:
            case 'multipart/form-data':
                handle_multipart(post_body, content_type)
            case 'text/uri-list':
                browse_new_tab(post_body.decode('utf-8'))
            case 'text/plain':
                match choose(["Copy to Clipboard", "Open in Browser"], 'text'):
                    case 0:
                        to_clipboard(post_body)
                    case 1:
                        browse_new_tab(
                            write_temp_file(post_body, '.txt', the_title)
                        )
            case 'application/x-basic-entity':
                realm_ctx = self.headers.get('X-Realm-Ctx')
                realm_ctx_dir = self.headers.get('X-Realm-Ctx-Dir')
                handler_send_entity.send_entity(
                    realm_ctx, realm_ctx_dir, post_body
                )

            case 'application/sql':
                match choose(["Copy to Clipboard", "Open in Browser"], 'text'):
                    case 0:
                        to_clipboard(post_body)
                    case 1:
                        browse_new_tab(
                            write_temp_file(post_body, '.sql.txt', the_title)
                        )
            case 'application/json-lines':
                handle_json_lines(post_body, the_title)

            case 'application/json':
                self.process_json(post_body, the_title)

        self.respond(200, 'application/json', json.dumps({}).encode('utf-8'))

    def process_json(self, post_body, the_title):
        data = json.loads(post_body.decode('utf-8'))
        match choose([
            "Copy to Clipboard",
            "Open in Browser",
            "Open in IDEA",
            "Convert to YAML HTML and Open in Browser",
            "Convert to JSON HTML and Open in Browser",
            "Convert to YAML MD HTML and Copy to Clipboard",
            "Convert to JSON MD HTML and Copy to Clipboard",
            "Convert to BLOCK HTML and Open in Browser",
        ], 'JSON'):
            case 0:
                to_clipboard(post_body)
            case 1:
                browse_new_tab(
                    write_temp_file(post_body, '.json', the_title)
                )
            case 2:
                open_in_idea(
                    write_temp_file(post_body, '.json', the_title)
                )
            case 3:
                html_to_browser(
                    str(page_node(data, title_string=the_title)),
                    the_title
                )
            case 4:
                html_to_browser(
                    str(page_node(data, title_string=the_title, delegate=JsonNodeDelegateJson)),
                    the_title
                )
            case 5:
                to_clipboard(str(md_node(data)))
            case 6:
                to_clipboard(str(md_node(data, delegate=JsonNodeDelegateJson)))
            case 7:
                html_to_browser(
                    str(to_blocks_html(data, page_title=the_title)),
                    the_title
                )

    def respond(self, status, content_type, content):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(content)


httpd = HTTPServer(("0.0.0.0", SERVER_PORT), Server)

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
