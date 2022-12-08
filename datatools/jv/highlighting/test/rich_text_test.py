from datatools.tui.treeview.rich_text import Style, render_substr
from datatools.tui.ansi_str import ANSI_CMD_DEFAULT_FG, ANSI_CMD_ATTR_NOT_BOLD


def test__render_substr__1():
    spans = [('  ', Style()), ('{', Style())]
    assert render_substr(spans, 0, 10) == \
           '  ' + ANSI_CMD_DEFAULT_FG + ANSI_CMD_ATTR_NOT_BOLD + \
           '{' + ANSI_CMD_DEFAULT_FG + ANSI_CMD_ATTR_NOT_BOLD + '       '
    assert render_substr(spans, 1, 11) == \
           ' ' + ANSI_CMD_DEFAULT_FG + ANSI_CMD_ATTR_NOT_BOLD + \
           '{' + ANSI_CMD_DEFAULT_FG + ANSI_CMD_ATTR_NOT_BOLD + '        '
    assert render_substr(spans, 2, 12) == \
           '{' + ANSI_CMD_DEFAULT_FG + ANSI_CMD_ATTR_NOT_BOLD + '         '
    assert render_substr(spans, 4, 14) == '          '
