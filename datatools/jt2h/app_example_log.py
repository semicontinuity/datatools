#!/usr/bin/env python3
from datetime import datetime

from datatools.jt2h.app import page_node, data
from datatools.jt2h.ats_channels import channel_deleted, channel_created, channel_color, channel_event_type, channel_use
from datatools.jt2h.column_renderer_colored import ColumnRendererColored
from datatools.jt2h.column_renderer_custom import ColumnRendererCustom
from datatools.jt2h.column_renderer_entities_lifecycle import ColumnRendererEntitiesLifecycle
from util.html.elements import span


def main():
    j = data()
    print(page_node(j, column_renderers_ats(j)))


def column_renderers_ats(j):
    return [
        ColumnRendererCustom('time', False, lambda row: span(datetime.fromisoformat(row['time']).astimezone().strftime('%H:%M:%S.%f'))),
        ColumnRendererColored('level', True, j),
        ColumnRendererColored('requestID', True, j),
        ColumnRendererColored('method', False, j),
        ColumnRendererEntitiesLifecycle('ch', False, j, channel_color, channel_created, channel_deleted, channel_use),
        ColumnRendererCustom('event', False, lambda row: span(channel_event_type(row))),
        ColumnRendererColored('msg', False, j),
    ]


if __name__ == "__main__":
    main()
