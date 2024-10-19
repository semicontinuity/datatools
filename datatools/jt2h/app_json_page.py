#!/usr/bin/env python3
import json
import sys

from datatools.jt2h.json_node import JsonNode
from datatools.jt2h.json_node_css import JSON_NODE_CSS
from datatools.jt2h.json_node_delegate_yaml import JsonNodeDelegateYaml
from util.html.elements import html, body, head, style


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def page_node(contents):
    return html(
        head(
            style(
                '''
                body {
                    font-family: monospace; background-color: #e0e0e0;
                }
                ''',
                JSON_NODE_CSS,
            )
        ),
        body(
            contents
        )
    )


def main():
    print(
        page_node(
            JsonNode(data(), JsonNodeDelegateYaml())
        )
    )


if __name__ == '__main__':
    main()
