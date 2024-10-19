from datatools.jt2h.json_node_delegate import JsonNodeDelegate
from util.html.elements import div


class JsonNodeDelegateYaml(JsonNodeDelegate):

    def key_repr(self, key):
        return key

    def simple_node(self, v, key: str, key_space: int, last: bool):
        return div(
            self.indent(),
            self.key(key, key_space),
            self.primitive(v),
        )

    def complex_node_start(self, key: str, key_space: int, start: str):
        if key:
            res = div(
                self.indent(), self.key(key, key_space)
            )
            self.cur_indent += 2
            return res

    def complex_node_end(self, end: str, last: bool):
        self.cur_indent -= 2
