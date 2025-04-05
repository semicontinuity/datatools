import http.client
import os
import re
import subprocess
import sys
from datetime import datetime

import requests
from requests import Response

from datatools.intent import get_local_ip, SERVER_PORT
from datatools.intent.target_folder import get_target_folder
from datatools.util.subprocess import exe


# browse_url is buggy/hacky
def browse(url: str):
    if type(url) is str:
        url = url.encode('utf-8')
    exe(
        os.environ['HOME'],
        ['browse_url'],
        {},
        url
    )


def open_in_idea(path: str):
    conn = http.client.HTTPConnection("localhost", 63342)
    conn.request(
        method="GET",
        url=f"/api/file/{path}",
    )
    conn.getresponse()
    conn.close()


def to_clipboard(s):
    if type(s) is str:
        s = s.encode('utf-8')
    subprocess.run(['xclip', '-selection', 'clipboard'], input=s, stdout=subprocess.DEVNULL)


def convert_to_filename(input_string):
    sanitized = input_string.replace(' ', '_')
    sanitized = sanitized.replace('=', '_')
    sanitized = sanitized.replace(':', '_')
    sanitized = sanitized.replace(';', '_')
    sanitized = re.sub(r'[^\w\-]', '', sanitized)  # Retains letters, digits, underscores, and hyphens
    sanitized = sanitized.strip('_.')
    return sanitized


def write_temp_file(contents: bytes, suffix: str, name_base: str | None = None):
    folder = get_target_folder()
    file_name = write_temp_file_to(folder, contents, suffix, name_base)
    return folder + '/' + file_name


def write_temp_file_to(folder: str, contents: bytes, suffix: str, name_base: str | None = None):
    path = None
    if name_base:
        name_base = convert_to_filename(name_base)
    if name_base:
        path = folder + '/' + datetime.now().strftime('%y%m%d_%H%M%S__') + name_base + suffix
        if os.path.exists(path):
            path = None
    if path:
        with open(path, 'wb') as file:
            file.write(contents)
        return os.path.basename(path)
    else:
        import tempfile
        fd, path = tempfile.mkstemp(suffix=suffix, prefix="temp", dir=folder, text=True)
        with os.fdopen(fd, 'w+b') as tmp:
            tmp.write(contents)
        return os.path.basename(path)


def kiosk_open_url(url) -> Response | None:
    kiosk_endpoint = os.environ.get('KIOSK_ENDPOINT')
    if kiosk_endpoint:
        try:
            return requests.request(
                'POST',
                '%s' % kiosk_endpoint,
                headers={"Content-Type": "text/uri-list"},
                data=url,
            )
        except:
            print('kiosk connection refused', kiosk_endpoint)
            return None


def browse_new_tab(url: str):
    print(url, file=sys.stderr)
    kiosk_result = kiosk_open_url(url)
    if kiosk_result:
        print(kiosk_result.status_code, file=sys.stderr)
    else:
        exe(
            os.environ['HOME'],
            ['firefox', url],
            {},
        )


def html_to_browser(html: str|bytes, title: str | None = None):
    contents = html.encode('utf-8') if type(html) is str else html
    file_name = write_temp_file_to(get_target_folder(), contents, '.html', title)
    browse_new_tab(f'http://{get_local_ip()}:{SERVER_PORT}/{file_name}')
