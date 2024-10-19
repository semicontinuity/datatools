from typing import Hashable

import mmh3

from datatools.json.coloring_hash import color_string, hash_to_rgb, hash_to_rgb_dark
from datatools.json.util import escape
from util.html.elements import span, div


class JsonNode:
    j: Hashable

    def __init__(self, j):
        self.j = j

    def __str__(self) -> str:
        return str(self.json_node(self.j))

    @staticmethod
    def key_color_style(indent: int):
        return JsonNode.style_for_indent(indent, offset=0xE0)

    @staticmethod
    def style_for_indent(indent: int, offset: int):
        return 'background-color: ' + color_string(hash_to_rgb(mmh3.hash(str(indent), 1), offset=offset))

    @staticmethod
    def json_indent(indent: int):
        if indent > 0:
            return span('&nbsp;' * indent)

    @staticmethod
    def json_key(indent: int, key: str, key_space: int):
        if type(key) is str:
            return [
                span('"' + key + '"', '&nbsp;' * (key_space - len(key)), clazz='key', style=JsonNode.key_color_style(indent)),
                span(' : '),
            ]

    @staticmethod
    def json_primitive(v):
        if v is None:
            return span('null', clazz='null')
        elif type(v) is str:
            return span('"' + ''.join([escape(c) for c in v]) + '"', clazz='string')
        elif v is True:
            return span('true', clazz='true')
        elif v is False:
            return span('false', clazz='false')
        else:
            return span(v, clazz='number')

    def json_simple_node(self, v, key: str, key_space: int, indent: int, last: bool):
        return div(
            self.json_indent(indent),
            self.json_key(indent, key, key_space),
            self.json_primitive(v),
            span(',', clazz='comma') if not last else None,
        )

    def json_complex_node(
            self,
            items,
            key: str,
            key_space: int,
            indent: int,
            start: str,
            end: str,
            content_key_space: int,
            last: bool,
            size: int):

        return \
            div(
                div(
                    self.json_indent(indent),
                    self.json_key(indent, key, key_space),
                    span(start)
                ),

                (
                    self.json_node(v, k, content_key_space, indent + 2, i == size - 1)
                    for i, (k, v) in enumerate(items)
                ),

                div(
                    self.json_indent(indent),
                    span(end),
                    span(',', clazz='comma') if not last else None
                ),
            )

    def json_node(self, v, key: str = None, key_space: int = 0, indent: int = 0, last: bool = True):
        if type(v) is dict:
            return self.json_complex_node(
                items=v.items(),
                key=key,
                key_space=key_space,
                indent=indent,
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
                indent=indent,
                start='[',
                end=']',
                content_key_space=0,
                last=last,
                size=len(v)
            )
        else:
            return self.json_simple_node(v, key, key_space, indent, last)
