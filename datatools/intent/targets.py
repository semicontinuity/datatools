import http.client
import os
import re
import subprocess
from datetime import datetime

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
        return path
    else:
        import tempfile
        fd, path = tempfile.mkstemp(suffix=suffix, prefix="temp", dir=folder, text=True)
        with os.fdopen(fd, 'w+b') as tmp:
            tmp.write(contents)
        return path


def browse_new_tab(url: str):
    exe(
        os.environ['HOME'],
        ['firefox', url],
        {},
    )


def html_to_browser(html: str, title: str | None = None):
    browse_new_tab(
        write_temp_file(
            html.encode('utf-8'),
            '.html',
            title,
        )
    )
