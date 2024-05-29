#!/usr/bin/env python3

import json
import sys

from datatools.tui.buffer.json2ansi_buffer import Buffer
from datatools.tui.terminal import screen_size_or_default

from datatools.tui.box_drawing_chars import LEFT_BORDER


def main():
    # j = data()
    buffer = Buffer(40, 20)
    buffer.draw_attrs_box(10, 5, 20, 10, Buffer.MASK_BG_CUSTOM)
    buffer.draw_bg_colors_box(10, 5, 20, 10, 64, 64, 64)
    buffer.draw_attrs_box(10, 5, 20, 1, Buffer.MASK_OVERLINE)

    for j in range(10):
        buffer.draw_text(10, 5 + j, LEFT_BORDER)

    screen_size = screen_size_or_default()
    buffer.flush(*screen_size)


def data():
    return json.load(sys.stdin)


if __name__ == "__main__":
    main()
