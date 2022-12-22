import json
import os
import sys

from datatools.util.pipe_peer_env_var import get_pipe_peer_env_var


def init_object_exporter():
    ObjectExporter.INSTANCE = AnnotatedObjectExporter() \
        if not os.isatty(1) and get_pipe_peer_env_var('SUPPORTS_STRUCTURED_INPUT') else PlainObjectExporter()


class ObjectExporter:
    INSTANCE: 'ObjectExporter'

    def export(self, object, metadata):
        pass


class PlainObjectExporter(ObjectExporter):
    def export(self, object, metadata):
        print(json.dumps(object))
        sys.stdout.flush()


class AnnotatedObjectExporter(ObjectExporter):
    def export(self, object, metadata):
        print()
        print(json.dumps(metadata))
        print(json.dumps(object))
        sys.stdout.flush()
