from datatools.json2ansi_toolkit.border_style import BorderStyle
from datatools.json2ansi_toolkit.style import Style


def default_style(bg_color=None):
    import os
    return Style(
        BorderStyle(int(os.environ.get("STYLE_TABLE_BORDER_TOP", "1"))),
        BorderStyle(int(os.environ.get("STYLE_HEADER_BORDER_TOP", "1"))),
        BorderStyle(int(os.environ.get("STYLE_CELL_BORDER_TOP", "1"))),
        bg_color
    )
