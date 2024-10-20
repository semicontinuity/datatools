from datatools.jt2h.json_node_delegate import JsonNodeDelegate
from util.html.elements import div, span


class JsonNodeDelegateYaml(JsonNodeDelegate):

    def simple_node(self, v, key: str, key_space: int, last: bool):
        return div(
            self.indent_node(),
            self.key(key, key_space),
            self.primitive(v),
        )

    # ------------------------------------------------------------------------------------------------------------------

    def object_node_start(self, key: str, max_key_size: int):
        return self.complex_node_start(key, max_key_size)

    def object_node_end(self, key: str, last: bool):
        self.complex_node_end(key)

    # ------------------------------------------------------------------------------------------------------------------

    def array_node_start(self, key: str, max_key_size: int):
        return self.complex_node_start(key, max_key_size)

    def array_node_end(self, key: str, last: bool):
        self.complex_node_end(key)

    # ------------------------------------------------------------------------------------------------------------------

    def complex_node_start(self, key, max_key_size):
        res = []
        if type(key) is str:
            res.append(
                div(self.indent_node(), self.key(key, max_key_size))
            )
            self.cur_indent += 1
        elif type(key) is int:
            res.append(
                div(self.indent_node(), span('-', style=self.style_for_indent()))
            )
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
            return [span('-', style=self.style_for_indent()), ' ']

    def key_repr(self, key):
        return key
