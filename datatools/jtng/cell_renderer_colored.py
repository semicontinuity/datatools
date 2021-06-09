from typing import Sequence

from datatools.jt.auto_metadata import ColumnMetadata
from datatools.jt.auto_presentation import COLORING_NONE, COLORING_HASH_FREQUENT
from datatools.jt.themes import COLORS, ColorKey
from datatools.jtng.column_state import ColumnState
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES
from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.tui.terminal import set_colors_cmd_bytes


# Can be in 2 states:
# normal: shown as 1 characters of left margin + text + 1 characters of right margin
# collapsed: shown as 1 full block character
class WColoredTextCellRenderer:
    full_block = b'\xE2\x96\x88'
    state: ColumnState

    def __init__(self, column_metadata: ColumnMetadata, column_presentation, max_content_width, column_state):
        self.max_content_width = max_content_width
        self.column_metadata = column_metadata
        self.column_presentation = column_presentation
        self.state = column_state

    def __len__(self):
        return 1 if self.state.collapsed else self.max_content_width + 2

    def __call__(self, is_under_cursor, max_width, start, end, value):
        attrs = COLORS[ColorKey.CURSOR] if is_under_cursor else self.compute_cell_attrs(value)

        if self.state.collapsed:
            return set_colors_cmd_bytes(*self.compute_cell_attrs(value)) + self.full_block
        else:
            value = '' if value is None else str(value)
            length = len(value)
            text = str(value)
            text += ' ' * (max_width - 2 - length)
            border_attrs = COLORS[ColorKey.CURSOR] if is_under_cursor else COLORS[ColorKey.BOX_DRAWING]
            buffer = bytearray()
            if start == 0:
                buffer += set_colors_cmd_bytes(*border_attrs) + LEFT_BORDER_BYTES
            if start < max_width - 1 and end > 1:
                buffer += set_colors_cmd_bytes(*attrs) + bytes(text[max(0, start - 1):end - 1], 'utf-8')
            if end == max_width:
                buffer += set_colors_cmd_bytes(*border_attrs) + b' '
            return buffer

    def compute_cell_attrs(self, value) -> Sequence[int]:
        text_colors = COLORS[ColorKey.TEXT]
        if self.column_presentation is None:   # complex column
            return text_colors if value is not None else COLORS[ColorKey.BOX_DRAWING]

        if value is None:
            return text_colors

        value = str(value)
        if self.column_presentation.coloring == COLORING_NONE or (
                self.column_presentation.coloring == COLORING_HASH_FREQUENT and value in self.column_metadata.unique_values):
            return text_colors

        fg = hash_to_rgb(hash_code(value))
        return fg[0], fg[1], fg[2], text_colors[3], text_colors[4], text_colors[5]

    def toggle(self):
        self.state.collapsed = not self.state.collapsed
