from typing import Hashable

from datatools.jt2h.json_node_delegate import JsonNodeDelegate
from util.html.elements import div


class JsonNode:
    j: Hashable
    delegate: JsonNodeDelegate

    def __init__(self, j, delegate: JsonNodeDelegate):
        self.j = j
        self.delegate = delegate

    def __str__(self) -> str:
        return str(self.json_node(self.j))

    def json_node(self, v, key = None, max_key_size: int = 0, last: bool = True):
        if type(v) is dict:
            child_max_key_size = max(len(k) for k in v) if v else 0

            return div(
                self.delegate.object_node_start(key, max_key_size,),

                [
                    self.json_node(v1, k1, child_max_key_size, i == len(v) - 1)
                    for i, (k1, v1) in enumerate(v.items())
                ],

                self.delegate.object_node_end(key, last),
            )
        elif type(v) is list:
            return div(
                self.delegate.array_node_start(key, max_key_size),
                [
                    self.json_node(v2, k2, 0, k2 == len(v) - 1)
                    for k2, v2 in enumerate(v)
                ],
                self.delegate.array_node_end(key, last),
            )
        else:
            return self.delegate.simple_node(v, key, max_key_size, last)
