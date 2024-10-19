import mmh3

from datatools.json.coloring_hash import color_string, hash_to_rgb
from datatools.json.util import escape
from util.html.elements import span, div


class JsonNodeDelegate:

    def __init__(self):
        self.cur_indent = 0

    def style_for_indent(self):
        return 'background-color: ' + color_string(hash_to_rgb(mmh3.hash(str(self.cur_indent), 0), offset=0xD0)) + ';'

    def indent(self):
        if self.cur_indent > 0:
            return span('&nbsp;' * self.cur_indent)

    def key(self, key: str, key_space: int):
        if type(key) is str:
            return self.key_str(key, key_space)

    def key_str(self, key, key_space):
        return [
            span(
                self.key_repr(key),
                '&nbsp;' * (key_space - len(key)),
                clazz='key',
                style=self.style_for_indent()
            ),
            span(' : '),
        ]

    def key_repr(self, key):
        return '"' + key + '"'

    def simple_node(self, v, key: str, key_space: int, last: bool):
        return div(
            self.indent(),
            self.key(key, key_space),
            self.primitive(v),
            span(',', clazz='comma') if not last else None,
        )

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

    def object_node(self, key, start, contents, end):
        return div(start, *contents, end)

    def object_node_start(self, key: str, key_space: int):
        res = div(
            self.indent(), self.key(key, key_space), span('{')
        )
        self.cur_indent += 2
        return res

    def object_node_end(self, key: str, last: bool):
        self.cur_indent -= 2
        res = div(
            self.indent(), span('}'), span(',', clazz='comma') if not last else None
        )
        return res

    def array_node(self, key, start, contents, end):
        return div(start, *contents, end)

    def array_node_start(self, key: str, max_key_size: int):
        res = div(
            self.indent(), self.key(key, max_key_size), span('[')
        )
        self.cur_indent += 2
        return res

    def array_node_end(self, key: str, last: bool):
        self.cur_indent -= 2
        res = div(
            self.indent(), span(']'), span(',', clazz='comma') if not last else None
        )
        return res
