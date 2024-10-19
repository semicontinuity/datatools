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

    def json_complex_node(
            self,
            items,
            key: str,
            key_space: int,
            start: str,
            end: str,
            content_key_space: int,
            last: bool,
            size: int):

        return \
            div(
                self.delegate.complex_node_start(key, key_space, start),

                [
                    self.json_node(v, k, content_key_space, i == size - 1)
                    for i, (k, v) in enumerate(items)
                ],

                self.delegate.complex_node_end(end, last),
            )

    def json_node(self, v, key: str = None, key_space: int = 0, last: bool = True):
        if type(v) is dict:
            return self.json_complex_node(
                items=v.items(),
                key=key,
                key_space=key_space,
                start='{',
                end='}',
                content_key_space=max(len(k) for k in v) if v else 0,
                last=last,
                size=len(v)
            )
        elif type(v) is list:
            return self.json_complex_node(
                items=enumerate(v),
                key=key,
                key_space=key_space,
                start='[',
                end=']',
                content_key_space=0,
                last=last,
                size=len(v)
            )
        else:
            return self.delegate.simple_node(v, key, key_space, last)
