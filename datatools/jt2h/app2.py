#!/usr/bin/env python3
import json
import sys

from datatools.json.util import escape
from util.html.elements import html, body, span, div, head, style


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def page_node(contents):
    return html(
        head(
            style('''
body {
    font-family: monospace; background-color: #e0f0fa;
}

.key {
    color: indigo; ;
}
.string {
    color: teal; font-weight: bold;
}
.number {
    color: darkred; font-weight: bold
}
.true {
    color: green; font-weight: bold; 
}
.false {
    color: brown; font-weight: bold; 
}
.null {
    color: black; font-weight: bold; 
}
'''
                  )
        ),
        body(
            contents
        )
    )


def json_indent(indent: int):
    if indent > 0:
        return span('&nbsp;' * indent)


def json_key(key: str, key_space: int):
    if type(key) is str:
        return [
            span('"' + key + '"', clazz='key'),
            span('&nbsp;' * (key_space - len(key))),
            span(' : '),
        ]


def json_complex_node(items, key: str, key_space: int, indent: int, start: str, end: str, content_key_space: int,
                      last: bool, size: int):
    return \
        div(
            div(
                json_indent(indent),
                json_key(key, key_space),
                span(start)
            ),

            (
                json_node(v, k, content_key_space, indent + 2, i == size - 1)
                for i, (k, v) in enumerate(items)
            ),

            div(
                json_indent(indent),
                span(end),
                ',' if not last else None
            ),
        )


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


def json_simple_node(v, key: str, key_space: int, indent: int, last: bool):
    return div(
        json_indent(indent),
        json_key(key, key_space),
        json_primitive(v),
        span(',') if not last else None,
    )


def json_node(v, key: str = None, key_space: int = 0, indent: int = 0, last: bool = True):
    if type(v) is dict:
        return json_complex_node(
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
        return json_complex_node(
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
        return json_simple_node(v, key, key_space, indent, last)


def main():
    print(
        page_node(
            json_node(
                data()
            )
        )
    )


if __name__ == '__main__':
    main()
