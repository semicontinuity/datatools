import http.client
from typing import AnyStr
import email.message

from datatools.intent import SERVER_PORT, get_local_ip
from datatools.intent.kiosk_scanner import get_kiosk_ip
from datatools.intent.response import Response

PROXY_TIMEOUT_SECONDS = 5

# Headers we set ourselves / must not copy verbatim to the upstream request.
_HOP_HEADERS = {'x-destination', 'host'}


def post_request_destination(headers: email.message.Message) -> str | None:
    """Return the kiosk IP this POST should be routed to, or None to handle locally."""
    if headers.get('X-Destination') != 'kiosk':
        return None
    kiosk_ip = get_kiosk_ip()
    if kiosk_ip and kiosk_ip != get_local_ip():
        return kiosk_ip
    return None


def route_post_request(dest: str, path: str, headers: email.message.Message, post_body: AnyStr) -> Response | None:
    """Proxy the POST to dest and return its mirrored response, or None on failure.

    The 'X-Destination' header is stripped from the upstream request.
    """
    out_headers = {k: v for k, v in headers.items() if k.lower() not in _HOP_HEADERS}
    out_headers['Host'] = f'{dest}:{SERVER_PORT}'

    conn = http.client.HTTPConnection(dest, SERVER_PORT, timeout=PROXY_TIMEOUT_SECONDS)
    try:
        conn.request('POST', path, body=post_body, headers=out_headers)
        resp = conn.getresponse()
        data = resp.read()
        content_type = resp.getheader('Content-Type', 'application/octet-stream')
        return Response(resp.status, content_type, data)
    except Exception as e:
        print(f'kiosk proxy to {dest} failed: {e}')
        return None
    finally:
        conn.close()
