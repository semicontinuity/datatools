from typing import Sequence

from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.tui.jt.auto_coloring import COLORING_NONE, COLORING_HASH_FREQUENT
from datatools.tui.jt.themes import COLORS, ColorKey
from datatools.tui.terminal import set_colors_cmd_bytes


class WColoredTextCellRenderer:
    full_block = '\u2588'

    def __init__(self, column_attrs, column_coloring):
        self.column_attrs = column_attrs
        self.column_coloring = column_coloring

    def __call__(self, is_under_cursor, max_width, start, end, value):
        if value is None:
            value = ''
        length = len(value)
        text = str(value[start:end])
        attrs = COLORS[ColorKey.CURSOR] if is_under_cursor else self.compute_cell_attrs(value)
        return set_colors_cmd_bytes(*attrs) + bytes(text, 'utf-8') + b' ' * (max_width - length)

    def compute_cell_attrs(self, text) -> Sequence[int]:
        text_colors = COLORS[ColorKey.TEXT]

        if self.column_coloring == COLORING_NONE or (
                self.column_coloring == COLORING_HASH_FREQUENT and self.column_attrs.value_stats[text] <= 1):
            return text_colors

        fg = hash_to_rgb(hash_code(text))
        return fg[0], fg[1], fg[2], text_colors[3], text_colors[4], text_colors[5]
