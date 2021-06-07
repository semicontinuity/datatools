from typing import Sequence

from datatools.jt.auto_coloring import COLORING_NONE, COLORING_HASH_FREQUENT
from datatools.jt.themes import COLORS, ColorKey
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES
from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.tui.terminal import set_colors_cmd_bytes


class WColoredTextCellRenderer:
    full_block = '\u2588'

    def __init__(self, column_attrs):
        self.column_attrs = column_attrs

    def __call__(self, is_under_cursor, max_width, start, end, value):
        if value is None:
            value = ''
        length = len(value)
        text = str(value) + ' ' * (max_width - 2 - length)
        border_attrs = COLORS[ColorKey.CURSOR] if is_under_cursor else COLORS[ColorKey.BOX_DRAWING]
        attrs = COLORS[ColorKey.CURSOR] if is_under_cursor else self.compute_cell_attrs(value)
        buffer = bytearray()
        if start == 0:
            buffer += set_colors_cmd_bytes(*border_attrs) + LEFT_BORDER_BYTES
        if start < max_width - 1 and end > 1:
            buffer += set_colors_cmd_bytes(*attrs) + bytes(text[max(0, start - 1):end - 1], 'utf-8')
        if end == max_width:
            buffer += set_colors_cmd_bytes(*border_attrs) + b' '
        return buffer

    def compute_cell_attrs(self, text) -> Sequence[int]:
        text_colors = COLORS[ColorKey.TEXT]

        if self.column_attrs.coloring == COLORING_NONE or (
                self.column_attrs.coloring == COLORING_HASH_FREQUENT and self.column_attrs.value_stats[text] <= 1):
            return text_colors

        fg = hash_to_rgb(hash_code(text))
        return fg[0], fg[1], fg[2], text_colors[3], text_colors[4], text_colors[5]
