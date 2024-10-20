from datatools.jt2h.json_node_delegate import JsonNodeDelegate
from util.html.elements import div, span, table, tr, td


class JsonNodeDelegateYaml2(JsonNodeDelegate):

    def simple_node(self, v, key: str, key_space: int, last: bool):
        return self.node(
            self.key(key, key_space),
            ' ',
            self.primitive(v),
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
                div(start),
                div(
                    span('&nbsp;'),
                    span(*contents, style='width: 100%;'),
                    style='display: flex;'
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

    def key(self, key: str, key_space: int):
        if type(key) is str:
            return self.key_str(key, key_space)
        elif type(key) is int:
            return span('-')

    def key_repr(self, key):
        return key

    def key_str(self, key, key_space):
        return [
            span(
                self.key_repr(key),
                '&nbsp;' * (key_space - len(key)),
                clazz='key',
            ),
            span(' :'),
        ]

    # ------------------------------------------------------------------------------------------------------------------

    def node(self, *c):
        return div(
            *c,
            style=self.style_for_indent() + 'padding-left: 0.5em; border-left: solid 0.1em darkgray; ',
        )