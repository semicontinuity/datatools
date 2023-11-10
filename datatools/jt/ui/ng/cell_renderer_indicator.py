from dataclasses import dataclass
from typing import Any, Optional, Tuple

from datatools.jt.model.attributes import MASK_ROW_CURSOR, MASK_ROW_EMPHASIZED, MASK_OVERLINE
from datatools.jt.model.presentation import ColumnRenderer
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.ng.column_focus_handler_highlight_rows import ColumnFocusHandlerHighlightRows
from datatools.jt.ui.ng.render_data import RenderData
from datatools.jt.ui.themes import COLORS2, ColorKey
from datatools.tui.ansi import DOUBLE_UNDERLINE_BYTES, OVERLINE_BYTES
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES, LEFT_THICK_BORDER_BYTES
from datatools.tui.coloring import decode_rgb, is_color_value
from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.tui.terminal import set_colors_cmd_bytes2


@dataclass
class ColumnRendererIndicator(ColumnRenderer):
    type = 'indicator'
    color: str = None
    highlight: bool = None
    separator: bool = None
    thick: bool = False

    def make_delegate(self, render_data: RenderData):
        return WIndicatorCellRenderer(render_data, self.color_rgb(), self.highlight, self.separator, self.thick)

    def color_rgb(self) -> Optional[Tuple[int, int, int]]:
        if is_color_value(self.color):
            return decode_rgb(self.color[1:])


class WIndicatorCellRenderer(WColumnRenderer):
    bg: Any = None

    def __init__(self, render_data: RenderData, bg: Optional[Tuple[int, int, int]], highlight, separator: bool, thick: bool = False):
        self.render_data = render_data
        self.bg = bg
        self.highlight = highlight
        self.separator = separator
        self.thick = thick
        if highlight:
            focus_handler = ColumnFocusHandlerHighlightRows(render_data)
            self.focus_handler = lambda: focus_handler
            # self.__getitem__ = focus_handler.__getitem__

    def __len__(self):
        return 1

    def __call__(self, row_attrs, column_width, start, end, value, row):
        buffer = bytearray()
        if row_attrs & MASK_ROW_CURSOR:
            buffer += DOUBLE_UNDERLINE_BYTES
        if row_attrs & MASK_OVERLINE:
            buffer += OVERLINE_BYTES

        buffer += set_colors_cmd_bytes2(
            COLORS2[ColorKey.BOX_DRAWING][0],
            self.bg_color(value, row_attrs & MASK_ROW_EMPHASIZED)
        )
        buffer += LEFT_THICK_BORDER_BYTES if self.thick else LEFT_BORDER_BYTES
        return buffer

    def bg_color(self, value, row_emphasized: bool):
        if value is None:
            return super().background_color(row_emphasized)

        if self.bg is None:
            if type(value) is dict or type(value) is list:
                return self.bg
            else:
                return hash_to_rgb(hash_code(value), offset=64)
        else:
            return self.bg

    def __getitem__(self, row):
        row_attrs = 0

        if hasattr(self, 'focus_handler'):
            row_attrs |= getattr(self, 'focus_handler')().__getitem__(row)

        if self.separator and row > 0 and self.value(row) != self.value(row - 1):
            row_attrs |= MASK_OVERLINE

        return row_attrs

    def value(self, row):
        return self.render_data.named_cell_value_f(row, self.render_data.column_key)
