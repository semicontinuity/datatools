from datatools.json.json2ansi_toolkit import *


def style():
    import os
    return Style(
        BorderStyle(int(os.environ.get("STYLE_TABLE_BORDER_TOP", "1"))),
        BorderStyle(int(os.environ.get("STYLE_HEADER_BORDER_TOP", "1"))),
        BorderStyle(int(os.environ.get("STYLE_CELL_BORDER_TOP", "1")))
    )
