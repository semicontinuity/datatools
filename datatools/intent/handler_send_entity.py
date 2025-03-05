import email.parser
import email.policy
import email.utils
import os
import re
from pathlib import Path

from datatools.dbview.x.util.pg_query import query_from_yaml


class HandlerSendEntity:
    MIME_TYPE = 'multipart/form-data'
    folder: str

    def handle(self, post_body: bytes, content_type: str):
        parts = self.parse_multipart(post_body, content_type)
        self.send_entity(
            realm_ctx=parts['realm-ctx'].decode('utf-8'),
            realm_ctx_dir=parts['realm-ctx-dir'].decode('utf-8'),
            query_str=parts['query'].decode('utf-8'),
            snapshot=parts['snapshot'],
        )

    @staticmethod
    def _parse_multipart(body: bytes, boundary: str) -> dict[str, bytes]:
        parts = {}
        boundary = boundary.encode('utf-8')
        parts_data = body.split(b'--' + boundary)

        for part in parts_data[1:-1]:  # Skip prologue and epilogue
            part = part.strip(b'\r\n')
            headers_end = part.find(b'\r\n\r\n')

            if headers_end == -1:
                continue  # Skip malformed parts

            headers = part[:headers_end]
            content = part[headers_end + 4:]

            # Parse headers with email parser
            header_parser = email.parser.BytesHeaderParser()
            headers_dict = dict(header_parser.parsebytes(headers))

            cd = headers_dict.get('Content-Disposition', '')
            name_match = re.search(r'name="([^"]+)"', cd)

            if not name_match:
                continue  # Skip parts without name

            name = name_match.group(1)
            parts[name] = content

        return parts

    def parse_multipart(self, body: bytes, content_type: str):
        match = re.search(r'boundary=([^;]+)', content_type)
        if not match:
            raise Exception('no boundary')
        boundary = match.group(1).strip('"')
        parts = self._parse_multipart(body, boundary)
        return parts

    def send_entity(self, realm_ctx: str, realm_ctx_dir: str, query_str: str, snapshot: bytes = None):

        # Construct entity_realm_path from entity
        query = query_from_yaml(query_str)
        if len(query.filter) == 1 and query.filter[0].op == '=':
            entity_realm_path = f'{query.table}/:{query.filter[0].column}/{query.filter[0].value}'
        else:
            entity_realm_path = f'{query.table}/{str(hash(query_str))}'

        # Construct the target realm path
        target_realm_path = f"{self.folder}/{realm_ctx}"
        os.makedirs(target_realm_path, exist_ok=True)

        # Calculate the realm reference
        realm_ref = os.path.relpath(
            realm_ctx_dir,
            target_realm_path
        )

        # Check if the context pointer file exists, create a symlink if not
        context_pointer = Path(f"{target_realm_path}/._")
        if not context_pointer.exists():
            os.symlink(realm_ref, context_pointer)

        # Construct the entity path
        entity_path = f"{target_realm_path}/{entity_realm_path}"
        os.makedirs(entity_path, exist_ok=True)

        # Process the query and save it to the `.query` file
        with Path(f"{entity_path}/.query").open('w') as f:
            f.write(query_str)

        if snapshot is not None:
            with Path(f"{entity_path}/snapshot.jsonl").open('w+b') as f:
                f.write(snapshot)
