import os
import sys
import time
import json
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from pathlib import Path
from typing import Tuple, Any
from insight.tiered_data_frame import TieredDataFrame, dmd_as_tiered_schema
import pandas as pd
import sys
from insight.app.annotate2 import tdf_from_aggregated_json, annotate, tweak_schema

static_root = os.getenv('INSIGHT_PATH') + '/src/main/web/semicontinuity/insight/web'
if static_root is None:
    print('View root not set', file=sys.stderr)
    sys.exit(1)

print('Loading data...', file=sys.stderr)
data = json.load(sys.stdin)
tdf = tdf_from_aggregated_json(data, '.', '-')
print('done', file=sys.stderr)

annotate(tdf)
tweak_schema(tdf)
print('done', file=sys.stderr)


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
        print(f'OPTIONS {self.path}', file=sys.stderr)
        resource = self.path[len("/insight/data/"):].split('?')[0]
        resource_parts = resource.split('/')
        tier_schema = tdf.schema_tiers[len(resource_parts) - 1]
        self.respond(200, 'application/javascript', json.dumps(tier_schema).encode('utf-8'))

    def load_tdf(self):

        column_names = [e['name'] for e in tier_schema]
        file = base_folder + '/' + resource + '.tsv'

        return pd.read_csv(
            file, header=None, names=column_names, index_col=False,
            sep='\t'
        )

    def metadata(self):
        resource = self.path[len("/insight/data/"):].split('?')[0]
        resource_parts = resource.split('/')
        base_folder, resource_name = '.', resource_parts[0]
        tiered_schema = dmd_as_tiered_schema(base_folder, resource_name)
        num_tiers = len(resource_parts)
        tier_schema = tiered_schema[num_tiers - 1]
        return base_folder, resource, tier_schema, resource_parts

    def node_column_names(self):
        return [e['name'] for e in self.schema_tier]


    def content_type_by_path(self, path) -> str:
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

    def serve_file(self, localpath):
        filepath = f'{static_root}{localpath}'
        if Path(filepath).is_file():
            data = open(filepath, mode='rb').read()
            return 200, self.content_type_by_path(self.path), data
        else:
            status, content_type, content = 404, 'text/plain', bytes(self.path, 'utf-8')

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

httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)

print('Ready', file=sys.stderr)
print(f'http://{HOST_NAME}:{PORT_NUMBER}/insight/view/index.html#{{"url":"tdf:.ext","prefix":"log"}}', flush=True)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
