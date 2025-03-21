from dataclasses import dataclass
from typing import Dict

from datatools.jt.model.attributes import MASK_ROW_CURSOR, MASK_ROW_EMPHASIZED, MASK_OVERLINE
from datatools.jt.model.presentation import ColumnRenderer
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.ng.column_focus_handler_highlight_rows import ColumnFocusHandlerHighlightRows
from datatools.jt.ui.ng.render_data import RenderData
from datatools.jt.ui.themes import COLORS2, ColorKey
from datatools.tui.ansi import DOUBLE_UNDERLINE_BYTES, OVERLINE_BYTES
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES, LEFT_BORDER
from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.tui.terminal import set_colors_cmd_bytes2


@dataclass
class ColumnRendererDictIndexHashColored(ColumnRenderer):
    type = 'dict-index-hash-colored'

    def make_delegate(self, render_data: RenderData):
        return WDictIndexCellRenderer(render_data)


class WDictIndexCellRenderer(WColumnRenderer):
    dictionary: Dict[str, int]
    render_data: RenderData

    def __init__(self, render_data: RenderData):
        self.render_data = render_data
        self.dictionary = render_data.column_values_info.dictionary
        self.title = render_data.column_presentation.title
        focus_handler = ColumnFocusHandlerHighlightRows(render_data)
        self.focus_handler = lambda: focus_handler
        self.__getitem__ = focus_handler.__getitem__

    def __str__(self):
        if len(self.title) < len(self.dictionary) + 1:
            return LEFT_BORDER
        else:
            return LEFT_BORDER + self.title

    def __len__(self):
        return len(self.dictionary)

    def __call__(self, row_attrs, column_width, start, end, value, row):
        buffer = bytearray()
        if row_attrs & MASK_ROW_CURSOR:
            buffer += DOUBLE_UNDERLINE_BYTES
        if row_attrs & MASK_OVERLINE:
            buffer += OVERLINE_BYTES

        index_of_value = self.dictionary.get(value)
        
        for i in range(start, end):
            fg = COLORS2[ColorKey.BOX_DRAWING][0]
            bg = hash_to_rgb(hash_code(value), offset=64) if index_of_value is not None and index_of_value == i else super().background_color(row_attrs & MASK_ROW_EMPHASIZED)
            buffer += set_colors_cmd_bytes2(fg, bg)
            buffer += (LEFT_BORDER_BYTES if i == 0 else b' ')

        return buffer
