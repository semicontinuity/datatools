from datatools.jt2h.json_node_delegate import JsonNodeDelegate
from datatools.jt2h.json_node_helper import style_for_indent, primitive_node
from util.html.elements import div, span


class JsonNodeDelegateYaml2(JsonNodeDelegate):

    def __init__(self):
        self.indent = 2
        self.cur_indent = 0

    # ------------------------------------------------------------------------------------------------------------------

    def simple_node(self, v, key: str, max_key_size: int, last: bool):
        return self.node(
            self.key(key, max_key_size),
            ' ',
            primitive_node(v),
        )

    # ------------------------------------------------------------------------------------------------------------------

    def object_node(self, key, start, contents, end):
        return self.complex_node(key, contents, start)

    def object_node_start(self, key: str, max_key_size: int):
        return self.complex_node_start(key, max_key_size)

    def object_node_end(self, key: str, last: bool):
        self.complex_node_end(key)

    # ------------------------------------------------------------------------------------------------------------------

    def array_node(self, key, start, contents, end):
        return self.complex_node(key, contents, start)

    def array_node_start(self, key: str, max_key_size: int):
        return self.complex_node_start(key, max_key_size)

    def array_node_end(self, key: str, last: bool):
        self.complex_node_end(key)

    # ------------------------------------------------------------------------------------------------------------------

    def complex_node(self, key, contents, start):
        if key is not None:
            return self.node(
                start,
                div(
                    span('&nbsp;'),
                    span(*contents, clazz='j-value'),
                    clazz='j-value-node',
                ),
            )
        else:
            return div(*contents)

    def complex_node_start(self, key, max_key_size):
        if key is not None:
            res = self.key(key, max_key_size)
            self.cur_indent += 1
            return res

    def complex_node_end(self, key):
        if key is not None:
            self.cur_indent -= 1

    # ------------------------------------------------------------------------------------------------------------------

    def node(self, *c):
        return div(
            *c,
            clazz='j-node',
            style=style_for_indent(self.cur_indent),
        )

    def key(self, key: str, max_key_size: int):
        if type(key) is str:
            return self.key_str(key, max_key_size)
        elif type(key) is int:
            return span('-')

    def key_str(self, key, max_key_size):
        return [
            span(
                self.key_repr(key),
                '&nbsp;' * (max_key_size - len(key)),
                clazz='key',
            ),
            span(' :'),
        ]

    def key_repr(self, key):
        return key
