import http.client
import json
import os
import subprocess
import sys


def init_object_exporter():
    ObjectExporter.INSTANCE = ObjectDispatcher()
    # ObjectExporter.INSTANCE = AnnotatedObjectExporter() \
    #     if not os.isatty(1) and get_pipe_peer_env_var('SUPPORTS_STRUCTURED_INPUT') else PlainObjectExporter()


class ObjectExporter:
    INSTANCE: 'ObjectExporter' = None

    def export(self, obj: str, metadata, channel):
        pass


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


class HttpObjectExporter(ObjectExporter):
    # @override
    def export(self, obj: str, metadata, channel):
        headers = {"x-env": json.dumps(os.environ)}
        conn = http.client.HTTPConnection("localhost", 8888)
        conn.request("POST", "", obj, headers)
        conn.getresponse()
        conn.close()


class HttpIntentObjectExporter(ObjectExporter):
    # @override
    def export(self, obj: str, metadata: dict[str, str], channel):
        headers = {"Content-Type": metadata.get('Content-Type') or "application/json"}
        conn = http.client.HTTPConnection("localhost", 7777)
        conn.request("POST", "", obj.encode('utf-8'), headers)
        conn.getresponse()
        conn.close()


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
