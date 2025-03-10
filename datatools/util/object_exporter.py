import http.client
import json
import os
import random
import string
import subprocess
import sys
from typing import Any


def init_object_exporter():
    ObjectExporter.INSTANCE = ObjectDispatcher()
    # ObjectExporter.INSTANCE = AnnotatedObjectExporter() \
    #     if not os.isatty(1) and get_pipe_peer_env_var('SUPPORTS_STRUCTURED_INPUT') else PlainObjectExporter()


class ObjectExporter:
    INSTANCE: 'ObjectExporter' = None

    def export(self, obj: str, metadata, channel):
        pass

    def export_multipart(self, data: dict[str, Any]):
        ...


class ObjectDispatcher(ObjectExporter):
    def __init__(self) -> None:
        self.exporter0 = HttpIntentObjectExporter()
        self.exporter1 = RunProcessObjectExporter()

    # @override
    def export(self, obj: str, metadata: dict[str, str], channel):
        if channel:
            self.exporter1.export(obj, metadata, channel)
        else:
            self.exporter0.export(obj, metadata, channel)

    def export_multipart(self, data: dict[str, Any]):
        self.exporter0.export_multipart(data)


class HttpObjectExporter(ObjectExporter):
    # @override
    def export(self, obj: str, metadata, channel):
        headers = {"x-env": json.dumps(os.environ)}
        conn = http.client.HTTPConnection("localhost", 8888)
        conn.request("POST", "", obj, headers)
        conn.getresponse()
        conn.close()


class HttpIntentObjectExporter(ObjectExporter):

    def export_multipart(self, data: dict[str, Any]):
        self.export(
            {k: v for k, v in data.items() if v is not None},
            {
                "Content-Type": "multipart/form-data",
            },
            0
        )

    # @override
    def export(self, obj: Any, metadata: dict[str, str], channel):
        conn = http.client.HTTPConnection("localhost", 7777)
        if metadata["Content-Type"] == "multipart/form-data" and type(obj) is dict:
            boundary = self.generate_boundary()
            conn.request(
                method="POST",
                url="",
                body=self.create_multipart_body(obj, {}, boundary=boundary),
                headers=({k: v for k, v in metadata.items() if v} | {
                    'Content-Type': f'multipart/form-data; boundary={boundary}'})
            )
        else:
            conn.request(
                method="POST",
                url="",
                body=obj.encode('utf-8'),
                headers={k: v for k, v in metadata.items() if v})
        conn.getresponse()
        conn.close()

    def generate_boundary(self):
        # Generate a random boundary string (25 characters)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=25))

    def create_multipart_body(self, fields, files, boundary):
        body = []
        CRLF = b'\r\n'

        # Add form fields
        for name, value in fields.items():
            body.append(f'--{boundary}'.encode())
            body.append(f'Content-Disposition: form-data; name="{name}"'.encode())
            body.append(b'')
            body.append(value.encode())

        # Add files
        for name, file_info in files.items():
            filename, filepath = file_info
            body.append(f'--{boundary}'.encode())
            body.append(
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode()
            )
            body.append(f'Content-Type: application/octet-stream'.encode())
            body.append(b'')

            with open(filepath, 'rb') as f:
                body.append(f.read())

        # Add closing boundary
        body.append(f'--{boundary}--'.encode())
        body.append(b'')

        return CRLF.join(body)


class PlainObjectExporter(ObjectExporter):
    # @override
    def export(self, obj: str, metadata, channel):
        print(obj)
        sys.stdout.flush()


class AnnotatedObjectExporter(ObjectExporter):
    # @override
    def export(self, obj: str, metadata, channel):
        # and not sys.stdout.isatty()
        print()
        print(json.dumps(metadata))
        print(obj)
        sys.stdout.flush()


class QtClipboardObjectExporter(ObjectExporter):
    def __init__(self) -> None:
        from PyQt5 import QtWidgets
        self.app = QtWidgets.QApplication(sys.argv)

    # @override
    def export(self, obj, metadata, channel):
        from PyQt5.QtCore import QMimeData
        from PyQt5.QtGui import QGuiApplication

        clipboard = QGuiApplication.clipboard()

        data = QMimeData()
        data.setData("application/json", b"1")
        data.setData("text/plain", b"1")
        clipboard.setMimeData(data)


class PyperclipObjectExporter(ObjectExporter):
    def export(self, obj, metadata, channel):
        import pyperclip
        pyperclip.copy("1")


class XClipObjectExporter(ObjectExporter):
    def export(self, obj, metadata, channel):
        from subprocess import run
        data = obj if type(obj) is str else json.dumps(obj)
        run(['xclip', '-selection', 'clipboard'], input=data.encode('utf-8'), stdout=subprocess.DEVNULL)


class RunProcessObjectExporter(ObjectExporter):
    def export(self, obj, metadata, channel):
        from subprocess import run
        from pathlib import Path
        exporter = Path(os.environ['HOME']) / '.config/datatools/export'
        if exporter.is_file() and os.access(exporter, os.X_OK):
            # env = os.environ | {'METADATA': json.dumps(metadata)}
            data = obj if type(obj) is str else json.dumps(obj)
            run([exporter], input=data.encode('utf-8'), stdout=subprocess.DEVNULL)
