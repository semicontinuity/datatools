from typing import Sequence

from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.jt.auto_presentation import COLORING_NONE, COLORING_HASH_FREQUENT
from datatools.jt.themes import COLORS, ColorKey
from datatools.tui.terminal import set_colors_cmd_bytes


class WColoredTextCellRenderer:
    full_block = '\u2588'

    def __init__(self, column_metadata, column_presentation):
        self.column_metadata = column_metadata
        self.column_presentation = column_presentation

    def __call__(self, is_under_cursor, max_width, start, end, value):
        if value is None:
            value = ''
        value = str(value)
        length = len(value)
        text = str(value[start:end])
        attrs = COLORS[ColorKey.CURSOR] if is_under_cursor else self.compute_cell_attrs(value)
        return set_colors_cmd_bytes(*attrs) + bytes(text, 'utf-8') + b' ' * (max_width - length)

    def compute_cell_attrs(self, text) -> Sequence[int]:
        text_colors = COLORS[ColorKey.TEXT]

        if self.column_presentation.coloring == COLORING_NONE or (
                self.column_presentation.coloring == COLORING_HASH_FREQUENT and text in self.column_metadata.unique_values):
            return text_colors

        fg = hash_to_rgb(hash_code(text))
        return fg[0], fg[1], fg[2], text_colors[3], text_colors[4], text_colors[5]
