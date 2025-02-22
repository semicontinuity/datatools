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

PAGE_CSS_X_LARGE = '''
body {
    background-color: #e0e0e0;
    display: inline-block;
}
span {
    font-size: x-large;
}
'''

PAGE_CSS_X_SMALL = '''
span {
    font-size: x-small;
}
'''

SPAN_CSS = '''
span {
    font-family: monospace; color: black;
}
'''


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def page_node(data, title_string: str = None, include_page_css: bool = True, delegate=JsonNodeDelegateYaml2):
    return PageNode(
        html(
            head(
                _title(title_string),
                style(
                    PAGE_CSS_X_LARGE if include_page_css else PAGE_CSS_X_SMALL,
                    SPAN_CSS,
                    JSON_NODE_HELPER_CSS,
                    JSON_NODE_DELEGATE_YAML_CSS,
                )
            ),
            body(
                JsonNode(data, delegate())
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
