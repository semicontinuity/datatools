import json
import os
import subprocess
import sys

from datatools.util.pipe_peer_env_var import get_pipe_peer_env_var


def init_object_exporter():
    ObjectExporter.INSTANCE = XClipObjectExporter()
    # ObjectExporter.INSTANCE = AnnotatedObjectExporter() \
    #     if not os.isatty(1) and get_pipe_peer_env_var('SUPPORTS_STRUCTURED_INPUT') else PlainObjectExporter()


class ObjectExporter:
    INSTANCE: 'ObjectExporter'

    def export(self, obj, metadata):
        pass


class PlainObjectExporter(ObjectExporter):
    def export(self, obj, metadata):
        print(json.dumps(obj))
        sys.stdout.flush()


class AnnotatedObjectExporter(ObjectExporter):
    def export(self, obj, metadata):
        # and not sys.stdout.isatty()
        print()
        print(json.dumps(metadata))
        print(json.dumps(obj))
        sys.stdout.flush()


class QtClipboardObjectExporter(ObjectExporter):

    def __init__(self) -> None:
        from PyQt5 import QtWidgets
        self.app = QtWidgets.QApplication(sys.argv)

    def export(self, obj, metadata):
        from PyQt5.QtCore import QMimeData
        from PyQt5.QtGui import QGuiApplication

        clipboard = QGuiApplication.clipboard()

        data = QMimeData()
        data.setData("application/json", b"1")
        data.setData("text/plain", b"1")
        clipboard.setMimeData(data)


class PyperclipObjectExporter(ObjectExporter):
    def export(self, obj, metadata):
        import pyperclip
        pyperclip.copy("1")


class XClipObjectExporter(ObjectExporter):
    def export(self, obj, metadata):
        from subprocess import run
        data = obj if type(obj) is str else json.dumps(obj)
        run(['xclip', '-selection', 'clipboard'], input=data.encode('utf-8'), stdout=subprocess.DEVNULL)
