#!/usr/bin/env python3
import json
import sys

from datatools.jt2h.column_renderer_colored import ColumnRendererColored
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
        ColumnRendererColored(j, 'time'),
        ColumnRendererColored(j, 'level'),
        ColumnRendererColored(j, 'method'),
        ColumnRendererColored(j, 'requestID'),
        ColumnRendererColored(j, 'msg'),
    ]
    contents = Log(j, column_renderers)
    print(page_node(len(column_renderers), contents))


if __name__ == "__main__":
    main()
