from typing import AnyStr, Tuple


def geometry(text: AnyStr, tab_size=4) -> Tuple[int, int]:
    width = 0
    height = 1
    x = 0
    for c in text:
        if c == '\n':
            x = 0
            height += 1
        elif c == '\t':
            x = (x + tab_size) // tab_size * tab_size
            width = max(width, x)
        else:
            x += 1
            width = max(width, x)
    return width, height
