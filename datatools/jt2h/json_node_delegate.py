import mmh3

from datatools.json.coloring_hash import color_string, hash_to_rgb
from datatools.json.util import escape
from util.html.elements import span


class JsonNodeDelegate:

    def __init__(self):
        self.indent = 2
        self.cur_indent = 0

    # ------------------------------------------------------------------------------------------------------------------

    def simple_node(self, v, key: str, key_space: int, last: bool):
        pass

    # ------------------------------------------------------------------------------------------------------------------

    def object_node(self, key, start, contents, end):
        pass

    def object_node_start(self, key: str, max_key_size: int):
        pass

    def object_node_end(self, key: str, last: bool):
        pass

    # ------------------------------------------------------------------------------------------------------------------

    def array_node(self, key, start, contents, end):
        pass

    def array_node_start(self, key: str, max_key_size: int):
        pass

    def array_node_end(self, key: str, last: bool):
        pass

    # ------------------------------------------------------------------------------------------------------------------

    def primitive(self, v):
        if v is None:
            return span('null', clazz='null')
        elif type(v) is str:
            return span('"' + ''.join([escape(c) for c in v]) + '"', clazz='string')
        elif v is True:
            return span('true', clazz='true')
        elif v is False:
            return span('false', clazz='false')
        else:
            return span(v, clazz='number')

    # ------------------------------------------------------------------------------------------------------------------

    def style_for_indent(self):
        return 'background-color: ' + color_string(hash_to_rgb(mmh3.hash(str(self.cur_indent), 0x10ADF00D), offset=0xD0)) + ';'
