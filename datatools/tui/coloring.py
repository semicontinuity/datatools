# For dark theme


def hash_code(s):
    """ Consistent hash """
    hh = 0
    for c in s:
        hh = (31 * hh + ord(c)) % 4294967296
    return hh


def hash_to_rgb(h):
    if h is None:
        return 0, 0, 0

    r6 = h % 2
    h = (h - r6) // 2
    g6 = h % 2
    h = (h - g6) // 2
    b6 = h % 2
    h = (h - g6) // 2

    r3 = h % 32
    h = (h - r3) // 32
    g3 = h % 32
    h = (h - g3) // 32
    b3 = h % 32

    return r6 * 32 + r3 + 128, g6 * 32 + g3 + 128, b6 * 32 + b3 + 128


def ansi_foreground_escape_code(r, g, b):
    return "\x1b[38;2;" + str(r) + ';' + str(g) + ';' + str(b) + 'm'


def ansi_background_escape_code(r, g, b):
    return "\x1b[48;2;" + str(r) + ';' + str(g) + ';' + str(b) + 'm'
