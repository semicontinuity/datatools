from datatools.tui.rich_text import Style, render_substr


def test__render_substr__1():
    spans = [('  ', Style()), ('{', Style())]
    assert render_substr(spans, 0, 10) == '  ' + '{' + '       '
    assert render_substr(spans, 1, 11) == ' ' + '{' + '        '
    assert render_substr(spans, 2, 12) == '{' + '         '
    assert render_substr(spans, 4, 14) == '          '
