import os
from typing import Tuple, List

FD_IN = 2
FD_OUT = 2

TCAP_132_COLUMNS = 1
TCAP_SIXEL = 4
TCAP_NATIONAL_REPLACEMENT_CHARSETS = 9


def init_tty():
    import tty, termios
    global ttyattr
    ttyattr = termios.tcgetattr(FD_IN)
    tty.setraw(FD_IN)


def deinit_tty():
    import termios
    termios.tcsetattr(FD_IN, termios.TCSANOW, ttyattr)


def read_screen_size():
    resp = query_terminal(b"\x1b[18t")
    assert resp.startswith(b"\x1b[8;") and resp[-1:] == b"t"
    parts = resp[:-1].split(b";")
    return int(parts[2]), int(parts[1])


def read_tcaps() -> Tuple[int, List[int]]:
    """
    Return terminal ID (e.g. 6 for VT100, 65 for VT525) + list of capabilities
    Must be invoked in RAW mode
    """
    resp = query_terminal(b"\x1b[c")
    parts = resp[3:-1].split(b';')
    return int(parts[0]), [int(p) for p in parts[1:]]


def query_terminal(query):
    import select, os
    os.write(FD_OUT, query)
    res = select.select([FD_IN], [], [], 0.05)[0]
    return os.read(FD_IN, 32)


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
