def hash_code(s):
    """ Consistent hash """
    hh = 0
    for c in s:
        hh = (31 * hh + ord(c)) % 4294967296
    return hh


def hash_to_rgb(h, offset=0xE0):
    if h is None:
        return 0, 0, 0

    r6 = (h % 2) & 1
    h = (h - r6) // 2
    g6 = (h % 2) & 1
    h = (h - g6) // 2
    b6 = (h % 2) & 1
    h = (h - b6) // 2

    r5 = (h % 2) & 1
    h = (h - r5) // 2
    g5 = (h % 2) & 1
    h = (h - g5) // 2
    b5 = (h % 2) & 1
    h = (h - b5) // 2

    r3 = (h % 3) & 0x3
    h = (h - r3) // 4
    g3 = (h % 3) & 0x3
    h = (h - g3) // 4
    b3 = (h % 3) & 0x3

    return r6*16 + r5*8 + r3 + offset, g6*16 + g5*8 + g3 + offset, b6*16 + b5*8 + b3 + offset


def hash_to_rgb_dark(h):
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

    return r6 * 32 + r3, g6 * 32 + g3, b6 * 32 + b3
