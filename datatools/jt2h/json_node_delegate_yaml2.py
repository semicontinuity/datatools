from datatools.jt2h.json_node_delegate import JsonNodeDelegate
from util.html.elements import div, span, table, tr, td


class JsonNodeDelegateYaml2(JsonNodeDelegate):

    def indent(self):
        pass

    def key_repr(self, key):
        return key

    def key_str(self, key, key_space):
        return [
            span(
                self.key_repr(key),
                '&nbsp;' * (key_space - len(key)),
                clazz='key',
                style=self.style_for_indent()
            ),
            span(' :'),
        ]

    def key(self, key: str, key_space: int):
        if type(key) is str:
            return self.key_str(key, key_space)
        elif type(key) is int:
            return span('-', style=self.style_for_indent())

    def simple_node(self, v, key: str, key_space: int, last: bool):
        return div(
            self.key(key, key_space),
            ' ',
            self.primitive(v),
            style=self.style_for_indent() + 'padding-left: 0.5em; border-left: solid 0.1em darkgray; ',
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
            return div(
                div(start),
                div(
                    span('&nbsp;'),
                    span(*contents, style='width: 100%;'),
                    style='display: flex;'
                ),
                style=self.style_for_indent() + 'padding-left: 0.5em; border-left: solid 0.1em darkgray;'
            )
        else:
            return div(*contents, style=self.style_for_indent())

    def complex_node_start(self, key, max_key_size):
        if type(key) is str:
            res = self.key_str(key, max_key_size)
            self.cur_indent += 2
            return res
        elif type(key) is int:
            res = span('-', style=self.style_for_indent())
            self.cur_indent += 2
            return res

    def complex_node_end(self, key):
        if key is not None:
            self.cur_indent -= 2
