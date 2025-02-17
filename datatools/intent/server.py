#!/usr/bin/python3
"""
Intents HTTP server.
Decouples intents, triggered in datatools apps, from their effects.

HTTP server accepts entity as the body of HTTP POST request,
and reacts, depending on Content-Type
"""

import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from datatools.intent.popup_selector import choose
from datatools.jt2h.app import page_node_basic_auto, page_node_auto, md_table_node
from datatools.jt2h.app_json_page import page_node, md_node
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
                self.browse_new_tab(post_body)
            case 'text/plain':
                match choose(["Copy to Clipboard", "Open in Browser"], 'text'):
                    case 0:
                        self.to_clipboard(post_body)
                    case 1:
                        self.browse_new_tab(
                            self.write_temp_file(post_body, '.txt')
                        )
            case 'application/sql':
                match choose(["Copy to Clipboard", "Open in Browser"], 'text'):
                    case 0:
                        self.to_clipboard(post_body)
                    case 1:
                        self.browse_new_tab(
                            self.write_temp_file(post_body, '.sql.txt')
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
                        self.html_to_browser(str(page_node_auto(lines)))
                    case 2:
                        self.to_clipboard(str(page_node_auto(lines)))
                    case 3:
                        self.html_to_browser(str(page_node_basic_auto(lines)))
                    case 4:
                        self.to_clipboard(str(page_node_basic_auto(lines)))
                    case 5:
                        self.to_clipboard(str(md_table_node(lines)))

            case 'application/json':
                s = post_body.decode('utf-8')
                data = json.loads(s)
                match choose([
                    "Copy to Clipboard",
                    "Open in Browser",
                    "Convert to HTML and Open in Browser",
                    "Convert to MD HTML and Copy to Clipboard",
                ], 'JSON'):
                    case 0:
                        self.to_clipboard(post_body)
                    case 1:
                        self.browse_new_tab(
                            self.write_temp_file(post_body, '.json')
                        )
                    case 2:
                        self.html_to_browser(str(page_node(data)))
                    case 3:
                        self.to_clipboard(str(md_node(data)))

        self.respond(200, 'application/json', json.dumps({}).encode('utf-8'))

    def to_clipboard(self, s):
        if type(s) is str:
            s = s.encode('utf-8')
        subprocess.run(['xclip', '-selection', 'clipboard'], input=s, stdout=subprocess.DEVNULL)

    def html_to_browser(self, html):
        self.browse_new_tab(
            self.write_temp_file(
                html.encode('utf-8'),
                '.html'
            )
        )

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


httpd = HTTPServer(("localhost", 7777), Server)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
