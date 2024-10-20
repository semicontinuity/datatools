#!/usr/bin/env python3
import json
import sys
from datetime import datetime

from datatools.jt2h.ats_channels import channel_deleted, channel_created, channel_color, channel_event_type, channel_use
from datatools.jt2h.column_renderer_colored import ColumnRendererColored
from datatools.jt2h.column_renderer_custom import ColumnRendererCustom
from datatools.jt2h.column_renderer_entities_lifecycle import ColumnRendererEntitiesLifecycle
from datatools.jt2h.json_node_css import JSON_NODE_CSS
from datatools.jt2h.json_node_delegate_yaml2_css import YAML_NODE_CSS
from datatools.jt2h.log_node import LogNode
from datatools.jt2h.page_node import page_node
from datatools.jt2h.page_node_css import PAGE_NODE_CSS
from util.html.elements import span


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def main():
    j = data()

    column_renderers = [
        ColumnRendererCustom('time', False, lambda row: span(datetime.fromisoformat(row['time']).astimezone().strftime('%H:%M:%S.%f'))),
        ColumnRendererColored('level', True, j),
        ColumnRendererColored('requestID', True, j),
        ColumnRendererColored('method', False, j),
        ColumnRendererEntitiesLifecycle('ch', False, j, channel_color, channel_created, channel_deleted, channel_use),
        ColumnRendererCustom('event', False, lambda row: span(channel_event_type(row))),
        ColumnRendererColored('msg', False, j),
    ]
    log = LogNode(j, column_renderers)

    print("""<!DOCTYPE html>""")
    print(
        page_node(
            contents=log,
            css=[PAGE_NODE_CSS, log.css(), JSON_NODE_CSS, YAML_NODE_CSS],
            js=LogNode.JS
        )
    )


if __name__ == "__main__":
    main()
