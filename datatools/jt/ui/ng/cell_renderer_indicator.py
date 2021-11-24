from dataclasses import dataclass
from typing import Any

from datatools.jt.model.attributes import MASK_ROW_CURSOR
from datatools.jt.model.column_state import ColumnState
from datatools.jt.model.metadata import ColumnMetadata
from datatools.jt.model.presentation import ColumnPresentation, ColumnRenderer
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.themes import COLORS2, ColorKey
from datatools.tui.ansi import DOUBLE_UNDERLINE_BYTES
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES
from datatools.tui.coloring import decode_rgb, is_color_value
from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.tui.terminal import set_colors_cmd_bytes2


@dataclass
class ColumnRendererIndicator(ColumnRenderer):
    type = 'indicator'
    color: str = None

    def make_delegate(self, column_metadata: ColumnMetadata, column_presentation: ColumnPresentation, column_state: ColumnState):
        return WIndicatorCellRenderer(self)


class WIndicatorCellRenderer(WColumnRenderer):
    bg: Any = None

    def __init__(self, column_renderer: ColumnRendererIndicator):
        if is_color_value(column_renderer.color):
            self.bg = decode_rgb(column_renderer.color[1:])

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
        if value is None:
            return COLORS2[ColorKey.BOX_DRAWING][1]

        if self.bg is None:
            if type(value) is dict or type(value) is list:
                return self.bg
            else:
                return hash_to_rgb(hash_code(value), offset=64)
        else:
            return self.bg
