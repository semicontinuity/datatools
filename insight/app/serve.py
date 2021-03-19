import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from pathlib import Path
from typing import Tuple, Any

import pandas as pd

from insight.tiered_data_frame import dmd_as_tiered_schema

if len(sys.argv) < 2:
    print('Data root not set', file=sys.stderr)
    sys.exit(1)
dataset_root = sys.argv[1]

static_root = os.getenv('INSIGHT_PATH') + '/src/main/web/semicontinuity/insight/web'
if static_root is None:
    print('View root not set', file=sys.stderr)
    sys.exit(1)


class Server(BaseHTTPRequestHandler):
    def do_HEAD(self):
        return

    def do_GET(self):
        self.respond(*self.handle_GET())

    def handle_GET(self):
        print(f'GET {self.path}', file=sys.stderr)
        if self.path.startswith("/insight/view") or self.path == "/favicon.ico":
            return self.handle_static()
        elif self.path.startswith("/insight/data"):
            df = self.load_tdf()
            j = df.to_json(orient='records')
            return 200, 'application/json', j.encode('utf-8')
        else:
            return 404, 'text/plain', bytes(self.path, 'utf-8')

    def do_POST(self):
        return

    def do_OPTIONS(self):
        print(f'OPTIONS {self.path}', file=sys.stderr)
        base_folder, resource, tier_schema = self.request_parts()
        self.respond(200, 'application/javascript', json.dumps(tier_schema).encode('utf-8'))

    def load_tdf(self):
        base_folder, resource, tier_schema = self.request_parts()
        column_names = [e['name'] for e in tier_schema]
        file = base_folder + '/' + resource + '.tsv'
        return pd.read_csv(
            file, header=None, names=column_names, index_col=False,
            sep='\t'
        )

    def request_parts(self):
        resource = self.path[len("/insight/data/"):].split('?')[0]
        resource_parts = resource.split('/')
        base_folder, resource_name = f'{dataset_root}', resource_parts[0]
        tiered_schema = dmd_as_tiered_schema(base_folder, resource_name)
        tier_schema = tiered_schema[len(resource_parts) - 1]
        return base_folder, resource, tier_schema

    @staticmethod
    def content_type_by_path(path) -> str:
        if path.endswith('.html'):
            return 'text/html'
        elif path.endswith('.css'):
            return 'text/css'
        elif path.endswith('.js'):
            return 'text/javascript'
        elif path.endswith('.ico'):
            return 'image/x-icon'
        else:
            return 'application/octet-stream'

    def serve_file(self, local_path):
        filepath = f'{static_root}{local_path}'
        if Path(filepath).is_file():
            data = open(filepath, mode='rb').read()
            return 200, self.content_type_by_path(self.path), data
        else:
            return 404, 'text/plain', bytes(self.path, 'utf-8')

    def handle_static(self) -> Tuple[int, str, Any]:
        print(self.path)
        if self.path == "/favicon.ico":
            return self.serve_file(self.path)
        else:
            return self.serve_file(self.path[len("/insight/view"):])

    def respond(self, status, content_type, content):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(content)


HOST_NAME = 'localhost'
PORT_NUMBER = 8000

if __name__ == '__main__':
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)

    if len(sys.argv) >= 3:
        dataset_name = sys.argv[2]
        print(
            f'http://{HOST_NAME}:{PORT_NUMBER}/insight/view/index.html#{{"url":"tdf:.ext","prefix":"{dataset_name}"}}',
            flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
