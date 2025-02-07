#!/usr/bin/env python3
import json
import sys
from collections import defaultdict

from datatools.json.util import is_primitive
from datatools.jt2h.column_renderer_colored import ColumnRendererColored
from datatools.jt2h.json_node_delegate_yaml2_css import JSON_NODE_DELEGATE_YAML_CSS
from datatools.jt2h.json_node_helper_css import JSON_NODE_HELPER_CSS
from datatools.jt2h.log_node import LogNode
from datatools.jt2h.log_node_js import LOG_NODE_JS
from datatools.jt2h.page_node_css import PAGE_NODE_CSS, TABLE_NODE_CSS
from util.html.elements import html, head, style, script, body, title
from util.html.md_html_node import MdHtmlNode
from util.html.page_node import PageNode


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def main():
    print(page_node_auto(data()))


def md_table_node(j):
    return MdHtmlNode(
        style(
            TABLE_NODE_CSS,
            LogNode.CSS_CORE
        ),
        LogNode(j, column_renderers_auto(j), dynamic_columns=False, dynamic_rows=False)
    )


def page_node_basic_auto(j, title_str: str = None):
    return PageNode(
        html(
            head(
                title(title_str),
                style(
                    PAGE_NODE_CSS,
                    TABLE_NODE_CSS,
                    LogNode.CSS_CORE,
                ),
            ),

            body(
                LogNode(j, column_renderers_auto(j), dynamic_columns=False, dynamic_rows=False)
            )
        )
    )


def page_node_auto(j, script_text: str|None = LOG_NODE_JS, title_str: str = None):
    return page_node(j, column_renderers_auto(j), script_text, title_str)


def page_node(j, renderers, script_text: str = LOG_NODE_JS, title_str: str = None):
    return page_node_for(LogNode(j, renderers), script_text, title_str)


def page_node_for(log_node, script_text: str, title_str: str):
    return PageNode(
        html(
            head(
                title(title_str),
                style(
                    PAGE_NODE_CSS,
                    TABLE_NODE_CSS,
                    log_node.css(),
                    JSON_NODE_HELPER_CSS,
                    JSON_NODE_DELEGATE_YAML_CSS
                ),
                script(script_text) if script_text else None
            ),

            body(
                log_node
            )
        )
    )


def column_renderers_auto(j):
    column_counts = defaultdict(int)
    complex_columns = set()

    for row in j:
        for k, v in row.items():
            if not is_primitive(v):
                complex_columns.add(k)
            column_counts[k] += 1

    return [
        ColumnRendererColored(k, column_counts[k] != len(j), j)
        for k in column_counts
        if k not in complex_columns
    ]


if __name__ == "__main__":
    main()
