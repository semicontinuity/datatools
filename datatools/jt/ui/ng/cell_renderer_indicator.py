from typing import Any

from datatools.jt.model.presentation import ColumnPresentation
from datatools.jt.ui.themes import COLORS2, ColorKey
from datatools.jt.model.attributes import MASK_ROW_CURSOR
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.tui.ansi import DOUBLE_UNDERLINE_BYTES
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES
from datatools.tui.coloring import decode_rgb, is_color_value
from datatools.tui.terminal import set_colors_cmd_bytes2


class WIndicatorCellRenderer(WColumnRenderer):
    bg: Any = None

    def __init__(self, column_presentation: ColumnPresentation):
        coloring = column_presentation.get_renderer().coloring
        if is_color_value(coloring):
            self.bg = decode_rgb(coloring[1:])

    def __len__(self):
        return 1

    def __call__(self, row_attrs, max_width, start, end, value, assistant_value):
        buffer = bytearray()
        if row_attrs & MASK_ROW_CURSOR:
            buffer += DOUBLE_UNDERLINE_BYTES
        buffer += set_colors_cmd_bytes2(
            COLORS2[ColorKey.BOX_DRAWING][0],
            self.bg_color(value)
        )
        buffer += LEFT_BORDER_BYTES
        return buffer

    def bg_color(self, value):
        if self.bg is not None and value is not None:
            return self.bg
        return COLORS2[ColorKey.TEXT][0] if value is not None else COLORS2[ColorKey.BOX_DRAWING][1]
