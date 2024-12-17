#!/usr/bin/env python3
import json
import sys

from datatools.jt2h.json_node import JsonNode
from datatools.jt2h.json_node_delegate_yaml2 import JsonNodeDelegateYaml2
from datatools.jt2h.json_node_delegate_yaml2_css import JSON_NODE_DELEGATE_YAML_CSS
from datatools.jt2h.json_node_helper_css import JSON_NODE_HELPER_CSS
from util.html.elements import html, body, head, style
from util.html.page_node import PageNode

PAGE_CSS = '''
body {
    font-family: monospace; background-color: #e0e0e0;
}
'''


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def page_node(data):
    return PageNode(
        html(
            head(
                style(
                    PAGE_CSS,
                    JSON_NODE_HELPER_CSS,
                    JSON_NODE_DELEGATE_YAML_CSS,
                )
            ),
            body(
                JsonNode(data, JsonNodeDelegateYaml2())
            )
        )
    )


def main():
    print(page_node(data()))


if __name__ == '__main__':
    main()
