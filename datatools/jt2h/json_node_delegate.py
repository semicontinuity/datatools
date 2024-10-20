import mmh3

from datatools.json.coloring_hash import color_string, hash_to_rgb
from datatools.json.util import escape
from util.html.elements import span


class JsonNodeDelegate:

    # ------------------------------------------------------------------------------------------------------------------

    def simple_node(self, v, key: str, max_key_size: int, last: bool):
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
