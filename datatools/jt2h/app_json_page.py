#!/usr/bin/env python3
import json
import sys

from datatools.jt2h.json_node import JsonNode
from datatools.jt2h.json_node_delegate_yaml2 import JsonNodeDelegateYaml2
from datatools.jt2h.json_node_delegate_yaml2_css import JSON_NODE_DELEGATE_YAML_CSS
from datatools.jt2h.json_node_helper_css import JSON_NODE_HELPER_CSS
from util.html.elements import html, body, head, style, title as _title
from util.html.md_html_node import MdHtmlNode
from util.html.page_node import PageNode

PAGE_CSS = '''
body {
    font-size: x-large; background-color: #e0e0e0;
}
'''
SPAN_CSS = '''
span {
    font-family: monospace;
}
'''


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def page_node(data, title_string: str = None):
    return PageNode(
        html(
            head(
                _title(title_string),
                style(
                    PAGE_CSS,
                    SPAN_CSS,
                    JSON_NODE_HELPER_CSS,
                    JSON_NODE_DELEGATE_YAML_CSS,
                )
            ),
            body(
                JsonNode(data, JsonNodeDelegateYaml2())
            )
        )
    )


def md_node(data):
    return MdHtmlNode(
        style(
            SPAN_CSS,
            JSON_NODE_HELPER_CSS,
            JSON_NODE_DELEGATE_YAML_CSS,
        ),
        JsonNode(data, JsonNodeDelegateYaml2())
    )


def main():
    print(page_node(data()))


if __name__ == '__main__':
    main()
