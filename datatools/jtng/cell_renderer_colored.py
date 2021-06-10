from typing import Sequence

from datatools.jt.auto_metadata import ColumnMetadata
from datatools.jt.auto_presentation import COLORING_NONE, COLORING_HASH_FREQUENT, ColumnPresentation, \
    COLORING_HASH_ASSISTANT_COLUMN
from datatools.jt.themes import ColorKey, COLORS2
from datatools.jtng.cell_renderer import DOUBLE_UNDERLINE_BYTES, WCellRenderer
from datatools.jtng.column_state import ColumnState
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES
from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.tui.terminal import set_colors_cmd_bytes2


# Can be in 2 states:
# normal: shown as 1 characters of left margin + text + 1 characters of right margin
# collapsed: shown as 1 full block character
class WColoredTextCellRenderer(WCellRenderer):
    state: ColumnState

    def __init__(self, column_metadata: ColumnMetadata, column_presentation: ColumnPresentation, max_content_width, column_state):
        self.max_content_width = max_content_width
        self.column_metadata = column_metadata
        self.column_presentation = column_presentation
        self.state = column_state

    def assistant(self):
        return self.column_presentation.assistant_column

    def toggle(self):
        self.state.collapsed = not self.state.collapsed

    def __len__(self):
        return 1 if self.state.collapsed else self.max_content_width + 2

    def __call__(self, is_under_cursor, max_width, start, end, value, assistant_value):
        if self.state.collapsed:
            cell_attrs = self.compute_cell_attrs(value, assistant_value, offset=64)
            return set_colors_cmd_bytes2(
                COLORS2[ColorKey.BOX_DRAWING][0],
                cell_attrs[0]
            ) + LEFT_BORDER_BYTES
        else:
            value = '' if value is None else str(value)
            length = len(value)
            text = str(value)
            text += ' ' * (max_width - 2 - length)
            buffer = bytearray()
            if is_under_cursor:
                buffer += DOUBLE_UNDERLINE_BYTES

            if start == 0:
                buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING]) + LEFT_BORDER_BYTES
            if start < max_width - 1 and end > 1:
                attrs = self.compute_cell_attrs(value, assistant_value)
                buffer += set_colors_cmd_bytes2(*attrs) + bytes(text[max(0, start - 1):end - 1], 'utf-8')
            if end == max_width:
                buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING]) + b' '

            return buffer

    def compute_cell_attrs(self, value, assistant_value, offset=128) -> Sequence[int]:
        text_attrs = COLORS2[ColorKey.TEXT]
        if value is None:
            return COLORS2[ColorKey.BOX_DRAWING][1], None

        value = str(value)
        if self.column_presentation.coloring == COLORING_NONE or (
                self.column_presentation.coloring == COLORING_HASH_FREQUENT and value in self.column_metadata.unique_values):
            return text_attrs

        v = assistant_value if self.column_presentation.coloring == COLORING_HASH_ASSISTANT_COLUMN else value
        fg = hash_to_rgb(hash_code(v), offset=offset)
        return fg, text_attrs[1]
