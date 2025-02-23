#!/usr/bin/python3
"""
Intents HTTP server.
Decouples intents, triggered in datatools apps, from their effects.

HTTP server accepts entity as the body of HTTP POST request,
and reacts, depending on Content-Type
"""

import http.client
import json
import os
import re
import socketserver
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from typing import Tuple

from datatools.intent.popup_selector import choose
from datatools.json.json2html import to_blocks_html
from datatools.jt2h.app import page_node_basic_auto, page_node_auto, md_table_node
from datatools.jt2h.app_json_page import page_node, md_node
from datatools.jt2h.json_node_delegate_json import JsonNodeDelegateJson
from datatools.util.subprocess import exe


def default_folder():
    return os.environ['HOME'] + '/boards'


folder = default_folder()


class Server(BaseHTTPRequestHandler):

    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer) -> None:
        super().__init__(request, client_address, server)

    def log_message(self, fmt, *args):
        return

    def respond_with_path(self, status, path):
        self.respond(status, 'text/plain', (path + '\n').encode('utf-8'))

    def do_DELETE(self):
        global folder
        folder = default_folder()
        self.respond_with_path(200, folder)

    def do_GET(self):
        self.respond_with_path(200, folder)

    def do_PUT(self):
        global folder
        content_len = int(self.headers.get('Content-Length'))
        path = self.rfile.read(content_len).decode('utf-8')

        if os.path.exists(path):
            folder = path
            self.respond_with_path(200, folder)
        else:
            self.respond_with_path(404, path)

    def do_POST(self):
        the_title = self.headers.get('X-Title')
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)

        match self.headers.get('Content-Type'):
            case 'text/uri-list':
                self.browse_new_tab(post_body)
            case 'text/plain':
                match choose(["Copy to Clipboard", "Open in Browser"], 'text'):
                    case 0:
                        self.to_clipboard(post_body)
                    case 1:
                        self.browse_new_tab(
                            self.write_temp_file(post_body, '.txt', the_title)
                        )
            case 'application/sql':
                match choose(["Copy to Clipboard", "Open in Browser"], 'text'):
                    case 0:
                        self.to_clipboard(post_body)
                    case 1:
                        self.browse_new_tab(
                            self.write_temp_file(post_body, '.sql.txt', the_title)
                        )
            case 'application/json-lines':
                lines = self.json_lines(post_body)
                match choose(
                    [
                        "Copy to Clipboard (json lines)",
                        "Convert to HTML (dynamic) and Open in Browser",
                        "Convert to HTML (dynamic) and Copy to Clipboard",
                        "Convert to HTML (static) and Open in Browser",
                        "Convert to HTML (static) and Copy to Clipboard",
                        "Convert to MD HTML and Copy to Clipboard",
                    ],
                    'table'
                ):
                    case 0:
                        self.to_clipboard(post_body)
                    case 1:
                        self.html_to_browser(str(page_node_auto(lines, title_str=the_title)), the_title)
                    case 2:
                        self.to_clipboard(str(page_node_auto(lines, title_str=the_title)))
                    case 3:
                        self.html_to_browser(str(page_node_basic_auto(lines, title_str=the_title)), the_title)
                    case 4:
                        self.to_clipboard(str(page_node_basic_auto(lines, title_str=the_title)))
                    case 5:
                        self.to_clipboard(str(md_table_node(lines)))

            case 'application/json':
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
                        self.to_clipboard(post_body)
                    case 1:
                        self.browse_new_tab(
                            self.write_temp_file(post_body, '.json', the_title)
                        )
                    case 2:
                        self.open_in_idea(
                            self.write_temp_file(post_body, '.json', the_title)
                        )
                    case 3:
                        self.html_to_browser(
                            str(page_node(data, title_string=the_title)),
                            the_title
                        )
                    case 4:
                        self.html_to_browser(
                            str(page_node(data, title_string=the_title, delegate=JsonNodeDelegateJson)),
                            the_title
                        )
                    case 5:
                        self.to_clipboard(str(md_node(data)))
                    case 6:
                        self.to_clipboard(str(md_node(data, delegate=JsonNodeDelegateJson)))
                    case 7:
                        self.html_to_browser(
                            str(to_blocks_html(data, page_title=the_title)),
                            the_title
                        )


        self.respond(200, 'application/json', json.dumps({}).encode('utf-8'))

    def to_clipboard(self, s):
        if type(s) is str:
            s = s.encode('utf-8')
        subprocess.run(['xclip', '-selection', 'clipboard'], input=s, stdout=subprocess.DEVNULL)

    def html_to_browser(self, html: str, title: str|None = None):
        self.browse_new_tab(
            self.write_temp_file(
                html.encode('utf-8'),
                '.html',
                title,
            )
        )

    def json_lines(self, data):
        decode = data.decode('utf-8')
        split = decode.split('\n')
        return [json.loads(s) for s in split if s]

    def write_temp_file(self, contents: bytes, suffix: str, name_base: str | None = None):
        path = None
        if name_base:
            name_base = self.convert_to_filename(name_base)
        if name_base:
            path = folder + '/' + datetime.now().strftime('%y%m%d_%H%M%S__') + name_base + suffix
            if os.path.exists(path):
                path = None

        if path:
            with open(path, 'wb') as file:
                file.write(contents)
            return path
        else:
            import tempfile
            fd, path = tempfile.mkstemp(suffix=suffix, prefix="temp", dir=folder, text=True)
            with os.fdopen(fd, 'w+b') as tmp:
                tmp.write(contents)
            return path

    def browse_new_tab(self, url: str):
        exe(
            os.environ['HOME'],
            ['firefox', url],
            {},
        )

    def open_in_idea(self, path: str):
        conn = http.client.HTTPConnection("localhost", 63342)
        conn.request(
            method="GET",
            url=f"/api/file/{path}",
        )
        conn.getresponse()
        conn.close()

    # browse_url is buggy/hacky
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

    def convert_to_filename(self, input_string):
        sanitized = input_string.replace(' ', '_')
        sanitized = sanitized.replace('=', '_')
        sanitized = sanitized.replace(':', '_')
        sanitized = sanitized.replace(';', '_')
        sanitized = re.sub(r'[^\w\-]', '', sanitized)  # Retains letters, digits, underscores, and hyphens
        sanitized = sanitized.strip('_.')
        return sanitized


httpd = HTTPServer(("localhost", 7777), Server)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
