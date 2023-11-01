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
    INSTANCE: 'ObjectExporter'

    def export(self, obj, metadata, channel):
        pass


class ObjectDispatcher:
    def __init__(self) -> None:
        self.exporter_clipboard = XClipObjectExporter()
        self.exporter_process = RunProcessObjectExporter()

    def export(self, obj, metadata, channel):
        if channel:
            self.exporter_process.export(obj, metadata, channel)
        else:
            self.exporter_clipboard.export(obj, metadata, channel)


class HttpObjectExporter(ObjectExporter):
    def export(self, obj, metadata, channel):
        headers = {"x-env": json.dumps(os.environ)}
        conn = http.client.HTTPConnection("localhost", 8888)
        conn.request("POST", "", json.dumps(obj), headers)
        conn.getresponse()
        conn.close()


class PlainObjectExporter(ObjectExporter):
    def export(self, obj, metadata, channel):
        print(json.dumps(obj))
        sys.stdout.flush()


class AnnotatedObjectExporter(ObjectExporter):
    def export(self, obj, metadata, channel):
        # and not sys.stdout.isatty()
        print()
        print(json.dumps(metadata))
        print(json.dumps(obj))
        sys.stdout.flush()


class QtClipboardObjectExporter(ObjectExporter):
    def __init__(self) -> None:
        from PyQt5 import QtWidgets
        self.app = QtWidgets.QApplication(sys.argv)

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
