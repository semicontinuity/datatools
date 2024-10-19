import mmh3

from datatools.json.coloring_hash import color_string, hash_to_rgb
from datatools.json.util import escape
from util.html.elements import span, div


class JsonNodeDelegate:

    def __init__(self):
        self.cur_indent = 0

    def style_for_indent(self, color_offset: int):
        return 'background-color: ' + color_string(hash_to_rgb(mmh3.hash(str(self.cur_indent), 1), offset=color_offset))

    def indent(self):
        if self.cur_indent > 0:
            return span('&nbsp;' * self.cur_indent)

    def key(self, key: str, key_space: int):
        if type(key) is str:
            return [
                span(
                    self.key_repr(key),
                    '&nbsp;' * (key_space - len(key)),
                    clazz='key',
                    style=self.style_for_indent(color_offset=0xE0)
                ),
                span(' : '),
            ]

    def key_repr(self, key):
        return '"' + key + '"'

    def simple_node(self, v, key: str, key_space: int, last: bool):
        # print(f'<div>@simple {key} {self.cur_indent}</div>')
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

    def complex_node_start(self, key: str, key_space: int, start: str):
        # print(f'<div>+start {key} {self.cur_indent}</div>')
        res = div(
            self.indent(), self.key(key, key_space), span(start)
        )
        self.cur_indent += 2
        # print(f'<div>-start {key} {self.cur_indent}</div>')
        return res

    def complex_node_end(self, end: str, last: bool):
        # print(f'<div>+end {self.cur_indent}</div>')
        self.cur_indent -= 2
        res = div(
            self.indent(), span(end), span(',', clazz='comma') if not last else None
        )
        # print(f'<div>-end {self.cur_indent}</div>')
        return res
