import email.parser
import email.policy
import email.utils
import json
import re

from datatools.intent.handler_json_lines import handle_json_lines
from datatools.intent.handler_send_entity import handler_send_entity


def handle_multipart(post_body: bytes, content_type: str):
    parts = parse_multipart(post_body, content_type)
    realm_ctx = parts.get('realm-ctx')
    realm_ctx_dir = parts.get('realm-ctx-dir')

    if realm_ctx and realm_ctx_dir:
        handler_send_entity.send_entity(
            realm_ctx=realm_ctx.decode('utf-8'),
            realm_ctx_dir=realm_ctx_dir.decode('utf-8'),
            query=parts['query'],
            content=parts['content'],
            rs_metadata=parts['result-set-metadata'],
        )
    else:
        handle_json_lines(
            parts['Content'],
            parts['X-Title'].decode('utf-8') if parts.get('X-Title') else None,
            json.loads(parts.get('Collapsed-Columns')),
        )


def parse_multipart(body: bytes, content_type: str) -> dict[str, bytes]:
    match = re.search(r'boundary=([^;]+)', content_type)
    if not match:
        raise Exception('no boundary')
    boundary = match.group(1).strip('"')
    return _parse_multipart(body, boundary)


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
