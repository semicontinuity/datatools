from typing import Tuple, List

from datatools.tui.picotui_patch import isatty, cursor_position
from datatools.tui.tui_fd import FD_TUI_IN, FD_TUI_OUT

TCAP_132_COLUMNS = 1
TCAP_SIXEL = 4
TCAP_NATIONAL_REPLACEMENT_CHARSETS = 9

tty_attr = None


def init_tty():
    import tty
    import termios
    global tty_attr
    tty_attr = termios.tcgetattr(FD_TUI_IN)
    tty.setraw(FD_TUI_IN)


def deinit_tty():
    import termios
    termios.tcsetattr(FD_TUI_IN, termios.TCSANOW, tty_attr)


def with_raw_terminal(code):
    try:
        init_tty()
        return code()
    finally:
        deinit_tty()


def read_screen_size():
    resp = query_terminal(b"\x1b[18t")
    if resp.startswith(b"\x1b[8;") and resp[-1:] == b"t":
        parts = resp[:-1].split(b";")
        return int(parts[2]), int(parts[1])
    return 100, 40


def screen_size_or_default(default=(1000, 10000)):
    if isatty():
        return with_raw_terminal(read_screen_size)
    return default


def cursor_position_or_default(default=(0, 0)):
    if isatty():
        return with_raw_terminal(cursor_position)
    return default


def read_tcaps() -> Tuple[int, List[int]]:
    """
    Return terminal ID (e.g. 6 for VT100, 65 for VT525) + list of capabilities
    Must be invoked in RAW model
    """
    resp = query_terminal(b"\x1b[c")
    parts = resp[3:-1].split(b';')
    return int(parts[0]), [int(p) for p in parts[1:]]


def query_terminal(query):
    import select, os
    os.write(FD_TUI_OUT, query)
    res = select.select([FD_TUI_IN], [], [], 0.05)[0]
    return os.read(FD_TUI_IN, 32)


def cmd_copy_rectangular_area(
        src_top_line,
        src_left_column_border,
        src_bottom_line_border,
        src_right_column_border,
        src_page_number,
        dst_top_line,
        dst_left_column_border,
        dst_page_number):
    """ DECCRA = CSI Pts;Pls;Pbs;Prs;Pps;Ptd;Pld;Ppd$v """
    return b'\x1b%d;%d;%d;%d;%d;%d;%d;%d$v' % (
        src_top_line,
        src_left_column_border,
        src_bottom_line_border,
        src_right_column_border,
        src_page_number,
        dst_top_line,
        dst_left_column_border,
        dst_page_number
    )


def ansi_goto_str(x, y):
    return "\x1b[%d;%dH" % (y + 1, x + 1)


def ansi_attr_bytes(*codes):
    return b'\x1b[' + b';'.join(codes) + b'm'


def ansi_foreground_escape_code(r, g, b) -> str:
    return "\x1b[38;2;" + str(r) + ';' + str(g) + ';' + str(b) + 'm'


def ansi_background_escape_code(r, g, b) -> str:
    return "\x1b[48;2;" + str(r) + ';' + str(g) + ';' + str(b) + 'm'


def ansi_fg_color_cmd_bytes(r, g, b):
    return b"\x1B[38;2;%d;%d;%dm" % (r, g, b)


def ansi_fg_color_cmd_bytes0(r, g, b):
    return b"38;2;%d;%d;%d" % (r, g, b)


def ansi_bg_color_cmd_bytes(r, g, b):
    return b"\x1B[48;2;%d;%d;%dm" % (r, g, b)


def ansi_bg_color_cmd_bytes0(r, g, b):
    return b"48;2;%d;%d;%d" % (r, g, b)


def set_colors_cmd_bytes(*c):
    """ 2 arguments: 16-color fg+bg; 6 values: 16M-color fg+bg """
    if len(c) == 2:
        return attr_color_cmd_bytes(*c)
    else:
        return ansi_fg_color_cmd_bytes(c[0], c[1], c[2]) + ansi_bg_color_cmd_bytes(c[3], c[4], c[5])


def set_colors_cmd_bytes2(fg=None, bg=None):
    b = bytearray()
    if fg is None and bg is None:
        return b

    b += b'\x1b['

    if fg is not None:
        if type(fg) is int:
            if fg > 8:
                b += b'1;%d' % (fg + 30 - 8)
            else:
                b += b'%d' % (fg + 30)
        else:
            b += ansi_fg_color_cmd_bytes0(*fg)

    if bg is not None:
        if fg is not None:
            b += b';'

        if type(bg) is int:
            b += b'%d' % (bg + 40)
        else:
            b += ansi_bg_color_cmd_bytes0(*bg)

    b += b'm'
    return b


def attr_color_cmd_bytes(fg, bg=-1):
    if bg == -1:
        bg = fg >> 4
        fg &= 0xf
    if bg is None:
        if fg > 8:
            return b"\x1b[%d;1m" % (fg + 30 - 8)
        else:
            return b"\x1b[%dm" % (fg + 30)
    else:
        assert bg <= 8
        if fg > 8:
            return b"\x1b[%d;%d;1m" % (fg + 30 - 8, bg + 40)
        else:
            return b"\x1b[0;%d;%dm" % (fg + 30, bg + 40)


def append_utf8str_fixed_width(to: bytearray, s: str, width: int):
    append_utf8str(to, s[:width])
    append_spaces(to, width - len(s))


def append_utf8str(to: bytearray, s: str):
    to += bytes(s, 'utf-8')


def append_spaces(to: bytearray, width: int):
    to += b' ' * width
