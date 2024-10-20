from typing import Hashable, Optional


class JsonNodeDelegate:

    # ------------------------------------------------------------------------------------------------------------------

    def simple_node(self, v, key: Optional[Hashable], max_key_size: int, last: bool):
        pass

    # ------------------------------------------------------------------------------------------------------------------

    def object_node(self, key: Optional[Hashable], start, contents, end):
        pass

    def object_node_start(self, key: Optional[Hashable], max_key_size: int):
        pass

    def object_node_end(self, key: Optional[Hashable], last: bool):
        pass

    # ------------------------------------------------------------------------------------------------------------------

    def array_node(self, key: Optional[Hashable], start, contents, end):
        pass

    def array_node_start(self, key: Optional[Hashable], max_key_size: int):
        pass

    def array_node_end(self, key: Optional[Hashable], last: bool):
        pass
