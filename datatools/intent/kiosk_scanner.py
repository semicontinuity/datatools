"""
Discovery of a 'kiosk' server on the local network.

The kiosk is just another instance of this same intent server, listening on
SERVER_PORT. A background daemon thread periodically scans nearby IP addresses
(the local IP's last octet +-10, excluding self) for a host accepting TCP
connections on SERVER_PORT. The first responder (lowest IP) becomes the kiosk.
"""

import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from datatools.intent import SERVER_PORT, get_local_ip


SCAN_INTERVAL_SECONDS = 300
OCTET_RANGE = 10
PROBE_TIMEOUT_SECONDS = 3

_lock = threading.Lock()
_kiosk_ip: str | None = None


def get_kiosk_ip() -> str | None:
    with _lock:
        return _kiosk_ip


def _set_kiosk_ip(ip: str | None):
    global _kiosk_ip
    with _lock:
        _kiosk_ip = ip


def _is_listening(ip: str) -> bool:
    try:
        with socket.create_connection((ip, SERVER_PORT), timeout=PROBE_TIMEOUT_SECONDS):
            return True
    except OSError:
        return False


def scan_for_kiosk() -> str | None:
    """Return the lowest nearby IP listening on SERVER_PORT, or None.

    Addresses are probed in parallel: a slow LAN can take seconds per TCP
    connect, and non-existent hosts block for the full timeout, so probing
    the ~20 candidates sequentially would be prohibitively slow.
    """
    self_ip = get_local_ip()
    parts = self_ip.split('.')
    if len(parts) != 4:
        return None

    prefix = '.'.join(parts[:3])
    base = int(parts[3])

    candidates = []
    for octet in range(base - OCTET_RANGE, base + OCTET_RANGE + 1):
        if octet < 1 or octet > 254:
            continue
        ip = f'{prefix}.{octet}'
        if ip == self_ip:
            continue
        candidates.append(ip)

    if not candidates:
        return None

    with ThreadPoolExecutor(max_workers=len(candidates)) as pool:
        listening = {ip: fut for ip, fut in ((ip, pool.submit(_is_listening, ip)) for ip in candidates)}
        found = [ip for ip, fut in listening.items() if fut.result()]

    return min(found, key=lambda ip: int(ip.split('.')[3])) if found else None


def _discovery_tick():
    found = scan_for_kiosk()
    _set_kiosk_ip(found)
    if found:
        print(f'kiosk discovered at {found}')
    else:
        print('kiosk not found')


def discovery_loop():
    while True:
        try:
            _discovery_tick()
        except Exception as e:
            print(f'kiosk discovery error: {e}')
        time.sleep(SCAN_INTERVAL_SECONDS)


def start_discovery_thread():
    thread = threading.Thread(target=discovery_loop, name='kiosk-discovery', daemon=True)
    thread.start()
    return thread
