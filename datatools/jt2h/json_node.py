from typing import Hashable

from datatools.jt2h.json_node_delegate import JsonNodeDelegate


class JsonNode:
    j: Hashable
    delegate: JsonNodeDelegate

    def __init__(self, j, delegate: JsonNodeDelegate):
        self.j = j
        self.delegate = delegate

    def __str__(self) -> str:
        return str(self.node(self.j))

    def node(self, v, key = None, max_key_size: int = 0, last: bool = True):
        if type(v) is dict:
            return self.object_node(v, key, max_key_size, last)
        elif type(v) is list:
            return self.array_node(v, key, last, max_key_size)
        else:
            return self.delegate.simple_node(v, key, max_key_size, last)

    def object_node(self, v, key, max_key_size, last):
        max_child_key_size = max(len(k) for k in v) if v else 0
        return self.delegate.object_node(
            key,

            self.delegate.object_node_start(key, max_key_size),
            [
                self.node(vv, kk, max_child_key_size, i == len(v) - 1)
                for i, (kk, vv) in enumerate(v.items())
            ],
            self.delegate.object_node_end(key, last),
        )

    def array_node(self, v, key, last, max_key_size):
        return self.delegate.array_node(
            key,

            self.delegate.array_node_start(key, max_key_size),
            [
                self.node(vv, kk, 0, kk == len(v) - 1)
                for kk, vv in enumerate(v)
            ],
            self.delegate.array_node_end(key, last),
        )
