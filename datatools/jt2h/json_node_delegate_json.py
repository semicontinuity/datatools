from typing import Hashable, Optional

from datatools.jt2h.json_node_delegate import JsonNodeDelegate

from datatools.jt2h.json_node_helper import style_for_indent, primitive_node
from datatools.util.html.elements import span, div


class JsonNodeDelegateJson(JsonNodeDelegate):

    def __init__(self):
        self.indent = 2
        self.cur_indent = 0

    # ------------------------------------------------------------------------------------------------------------------

    def simple_node(self, v, key: Optional[Hashable], max_key_size: int, last: bool):
        return div(
            self.indent_node(),
            self.key(key, max_key_size),
            primitive_node(v, for_json=True),
            span(',', clazz='comma') if not last else None,
        )

    # ------------------------------------------------------------------------------------------------------------------

    def object_node(self, key, start, contents, end):
        return self.complex_node(start, contents, end)

    def object_node_start(self, key: str, max_key_size: int):
        return self.complex_node_start(key, max_key_size, '{')

    def object_node_end(self, key: str, last: bool):
        return self.complex_node_end(last, '}')

    # ------------------------------------------------------------------------------------------------------------------

    def array_node(self, key, start, contents, end):
        return self.complex_node(start, contents, end)

    def array_node_start(self, key: str, max_key_size: int):
        return self.complex_node_start(key, max_key_size, '[')

    def array_node_end(self, key: str, last: bool):
        return self.complex_node_end(last, ']')

    # ------------------------------------------------------------------------------------------------------------------

    def complex_node(self, start, contents, end):
        return div(start, *contents, end)

    def complex_node_start(self, key, max_key_size, c: str):
        res = div(
            self.indent_node(), self.key(key, max_key_size), span(c)
        )
        self.cur_indent += 1
        return res

    def complex_node_end(self, last: bool, c: str):
        self.cur_indent -= 1
        res = div(
            self.indent_node(), span(c), span(',', clazz='comma') if not last else None
        )
        return res

    # ------------------------------------------------------------------------------------------------------------------

    def indent_node(self):
        if self.cur_indent > 0:
            return span('&nbsp;' * (self.cur_indent * self.indent))

    def key(self, key: Optional[str], max_key_size: int):
        if type(key) is str:
            return self.key_str(key, max_key_size)

    def key_str(self, key: Optional[str], max_key_size):
        return [
            span(
                self.key_repr(key),
                '&nbsp;' * (max_key_size - len(key)),
                clazz='key',
                style=style_for_indent(self.cur_indent)
            ),
            span(' : '),
        ]

    def key_repr(self, key: str):
        return '"' + key + '"'
