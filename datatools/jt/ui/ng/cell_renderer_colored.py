from dataclasses import dataclass
from typing import Sequence, Dict

from datatools.jt.model.attributes import MASK_ROW_CURSOR
from datatools.jt.model.presentation import ColumnRenderer
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.ng.render_data import RenderData
from datatools.jt.ui.themes import ColorKey, COLORS2
from datatools.tui.ansi import DOUBLE_UNDERLINE_BYTES
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES, LEFT_BORDER
from datatools.tui.coloring import hash_code, hash_to_rgb, decode_rgb
from datatools.tui.terminal import set_colors_cmd_bytes2


@dataclass
class ColumnRendererBase(ColumnRenderer):
    assistant_column: str = None
    color: str = None
    

@dataclass
class ColumnRendererColoredPlain(ColumnRendererBase):
    type = 'colored-plain'

    def make_delegate(self, render_data: RenderData):
        return WColoredTextCellRendererPlain(self, render_data)


@dataclass
class ColumnRendererColoredMapping(ColumnRendererColoredPlain):
    type = 'colored-mapping'
    colorMap: Dict[str, str] = None

    def make_delegate(self, render_data: RenderData):
        return WColoredTextCellRendererMapping(self, render_data)


@dataclass
class ColumnRendererColoredHash(ColumnRendererColoredPlain):
    type = 'colored-hash'
    onlyFrequent: bool = False

    def make_delegate(self, render_data: RenderData):
        return WColoredTextCellRendererHash(self, render_data)


class WColoredTextCellRenderer(WColumnRenderer):

    def __init__(self, column_renderer: ColumnRendererBase, render_data: RenderData):
        self.column_renderer = column_renderer
        self.render_data = render_data

    def assistant(self):
        return self.column_renderer.assistant_column

    def __str__(self):
        return LEFT_BORDER + self.render_data.column_presentation.title if self.render_data.column_presentation.title else LEFT_BORDER

    def __len__(self):
        if self.column_renderer.max_content_width is None:
            return 0    # Declared in presentation file, but never occurring in the data
        return self.column_renderer.max_content_width + 2

    def __call__(self, row_attrs, column_width, start, end, value, assistant_value, row) -> bytes:
        value = '' if value is None else str(value)
        length = len(value)
        text = str(value)
        text += ' ' * (column_width - 2 - length)
        buffer = bytearray()
        if row_attrs & MASK_ROW_CURSOR:
            buffer += DOUBLE_UNDERLINE_BYTES

        if start == 0:
            buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING]) + LEFT_BORDER_BYTES
        if start < column_width - 1 and end > 1:
            attrs = self.compute_cell_attrs(value, assistant_value)
            buffer += set_colors_cmd_bytes2(*attrs) + bytes(text[max(0, start - 1):end - 1], 'utf-8')
        if end == column_width:
            buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING]) + b' '

        return buffer

    def compute_cell_attrs(self, value, assistant_value) -> Sequence[int]:
        text_attrs = COLORS2[ColorKey.TEXT]
        if value is None:
            return COLORS2[ColorKey.BOX_DRAWING][1], None

        fg = self.compute_color(self.value_to_use(str(value), assistant_value))
        return fg, text_attrs[1]

    def compute_color(self, value):
        pass

    def text_color(self):
        if self.column_renderer.color is None:
            return COLORS2[ColorKey.TEXT][0]
        else:
            return decode_rgb(self.column_renderer.color.lstrip('#'))

    def value_to_use(self, value, assistant_value):
        return assistant_value if assistant_value is not None else value


class WColoredTextCellRendererPlain(WColoredTextCellRenderer):
    def compute_color(self, value):
        return self.text_color()


class WColoredTextCellRendererMapping(WColoredTextCellRenderer):
    def __init__(self, column_renderer: ColumnRendererColoredMapping, render_data: RenderData):
        super().__init__(column_renderer, render_data)
        self.column_renderer = column_renderer

    def compute_color(self, value):
        color = self.column_renderer.colorMap.get(value)
        if color is not None:
            return decode_rgb(color.lstrip('#'))
        else:
            return self.text_color()


class WColoredTextCellRendererHash(WColoredTextCellRenderer):
    def __init__(self, column_renderer: ColumnRendererColoredHash, render_data: RenderData):
        super().__init__(column_renderer, render_data)
        self.column_renderer = column_renderer

    def compute_color(self, value):
        if self.column_renderer.onlyFrequent and value in self.render_data.column_metadata.unique_values:
            return self.text_color()
        else:
            return hash_to_rgb(hash_code(value), offset=128)
