import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from pathlib import Path
from typing import Tuple, Any

from datatools.util.logging import debug
from insight.app.annotate2 import tdf_from_aggregated_json, annotate, tweak_schema
from insight.tiered_data_frame import dmd_as_tiered_schema

static_root = os.getenv('INSIGHT_PATH') + '/src/main/web/semicontinuity/insight/web'
if static_root is None:
    debug('View root not set')
    sys.exit(1)

debug('Loading data...')
data = json.load(sys.stdin)
tdf, analyse_column_present = tdf_from_aggregated_json(data, base_folder='.', out_resource_name='-')
debug(f'done')
debug(f'analyse_column_present={analyse_column_present}')
debug(f'tiers={len(tdf.schema_tiers)}')

if analyse_column_present:
    annotate(tdf)
    tweak_schema(tdf, json.loads(sys.argv[1]))  # columns_settings


class Server(BaseHTTPRequestHandler):
    def do_HEAD(self):
        return

    def do_GET(self):
        self.respond(*self.handle_GET())

    def handle_GET(self):
        debug(f'GET {self.path}')
        if self.path.startswith("/insight/view") or self.path == "/favicon.ico":
            return self.handle_static()
        elif self.path.startswith("/insight/data"):
            resource = self.path[len("/insight/data/"):].split('?')[0]
            resource_parts = resource.split('/')
            df = tdf.resolve_df(resource_parts[1:])
            j = df.to_json(orient='records')
            return 200, 'application/json', j.encode('utf-8')
        else:
            return 404, 'text/plain', bytes(self.path, 'utf-8')

    def do_POST(self):
        return

    def do_OPTIONS(self):
        debug(f'OPTIONS {self.path}')
        resource = self.path[len("/insight/data/"):].split('?')[0]
        resource_parts = resource.split('/')
        tier_schema = tdf.schema_tiers[len(resource_parts) - 1]
        self.respond(200, 'application/javascript', json.dumps(tier_schema).encode('utf-8'))

    def metadata(self):
        resource = self.path[len("/insight/data/"):].split('?')[0]
        resource_parts = resource.split('/')
        base_folder, resource_name = '.', resource_parts[0]
        tiered_schema = dmd_as_tiered_schema(base_folder, resource_name)
        num_tiers = len(resource_parts)
        tier_schema = tiered_schema[num_tiers - 1]
        return base_folder, resource, tier_schema, resource_parts

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
            return 200, self.content_type_by_path(self.path), open(filepath, mode='rb').read()
        else:
            return 404, 'text/plain', bytes(self.path, 'utf-8')

    def handle_static(self) -> Tuple[int, str, Any]:
        debug(self.path)
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

httpd = HTTPServer((HOST_NAME, 0), Server)

debug('Ready')
print(f'http://{httpd.server_name}:{httpd.server_port}/insight/view/index.html#{{"url":"tdf:.ext","prefix":"log"}}', flush=True)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
