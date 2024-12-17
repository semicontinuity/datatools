#!/usr/bin/env python3
import json
import sys
from collections import defaultdict
from datetime import datetime

from datatools.jt2h.ats_channels import channel_deleted, channel_created, channel_color, channel_event_type, channel_use
from datatools.jt2h.column_renderer_colored import ColumnRendererColored
from datatools.jt2h.column_renderer_custom import ColumnRendererCustom
from datatools.jt2h.column_renderer_entities_lifecycle import ColumnRendererEntitiesLifecycle
from datatools.jt2h.json_node_delegate_yaml2_css import JSON_NODE_DELEGATE_YAML_CSS
from datatools.jt2h.json_node_helper_css import JSON_NODE_HELPER_CSS
from datatools.jt2h.log_node import LogNode
from datatools.jt2h.log_node_js import LOG_NODE_JS
from datatools.jt2h.page_node_css import PAGE_NODE_CSS
from util.html.elements import span, html, head, style, script, body
from util.html.page_node import PageNode


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def main():
    j = data()
    print(page_node(j, column_renderers(j)))


def page_node(j, r):
    return page_node_for(LogNode(j, r))


def page_node_for(log_node):
    return PageNode(
        html(

            head(
                style(
                    PAGE_NODE_CSS,
                    log_node.css(),
                    JSON_NODE_HELPER_CSS,
                    JSON_NODE_DELEGATE_YAML_CSS
                ),
                script(LOG_NODE_JS)
            ),

            body(
                log_node
            )
        )
    )


def column_renderers(j):
    column_counts = defaultdict(int)

    for row in j:
        for k in row:
            column_counts[k] += 1

    return [
        ColumnRendererColored(k, column_counts[k] != len(j), j)
        for k in column_counts
    ]


if __name__ == "__main__":
    main()
