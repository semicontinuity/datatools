# For dark theme
from typing import Optional, Tuple


def hash_code(s):
    """ Consistent hash """
    if type(s) is int:
        return s
    if type(s) is bool:
        return int(s)
    hh = 0
    for c in s:
        hh = (31 * hh + ord(c)) % 4294967296
    return hh


def hash_to_rgb(h, offset=128, scale=1):
    """ Converts hash code to R,G,B values with a default range of 64 """
    if h is None:
        return 0, 0, 0

    r6 = h % 2
    h = h // 2
    g6 = h % 2
    h = h // 2
    b6 = h % 2
    h = h // 2

    r3 = h % 32
    h = (h - r3) // 32
    g3 = h % 32
    h = (h - g3) // 32
    b3 = h % 32

    return scale*(r6 * 32 + r3) + offset, scale*(g6 * 32 + g3) + offset, scale*(b6 * 32 + b3) + offset


def hash_to_rgb_32(h, offset=128, scale=1):
    """ Converts hash code to R,G,B values with a default range of 32 """
    if h is None:
        return 0, 0, 0

    r3 = h % 32
    h = h // 32
    g3 = h % 32
    h = h // 32
    b3 = h % 32

    return scale * r3 + offset, scale * g3 + offset, scale * b3 + offset


def is_color_value(c: Optional[str]):
    return c is not None and type(c) is str and c.startswith('#')


def decode_rgb(s) -> Tuple[int, int, int]:
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
