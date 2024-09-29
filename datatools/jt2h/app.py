#!/usr/bin/env python3
import json
import sys

from datatools.jt2h.ats_channels import channel_deleted, channel_created, channel_color, channel_used, \
    channel_event_type
from datatools.jt2h.column_renderer_colored import ColumnRendererColored
from datatools.jt2h.column_renderer_custom import ColumnRendererCustom
from datatools.jt2h.column_renderer_entities_lifecycle import ColumnRendererEntitiesLifecycle
from datatools.jt2h.log_node import Log
from datatools.jt2h.page_node import page_node


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j


def main():
    j = data()
    column_renderers = [
        ColumnRendererColored('time', False, j),
        ColumnRendererColored('level', True, j),
        ColumnRendererColored('method', False, j),
        ColumnRendererColored('requestID', True, j),
        ColumnRendererColored('msg', False, j),
        ColumnRendererEntitiesLifecycle('ch', False, channel_color, channel_created, channel_deleted, channel_used),
        ColumnRendererCustom('event', False, channel_event_type),
    ]
    contents = Log(j, column_renderers)
    print(page_node(len(column_renderers), contents))


if __name__ == "__main__":
    main()
