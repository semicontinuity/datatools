from dataclasses import dataclass
from typing import Dict

from datatools.jt.model.attributes import MASK_ROW_CURSOR, MASK_ROW_EMPHASIZED
from datatools.jt.model.presentation import ColumnRenderer
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.ng.render_data import RenderData
from datatools.jt.ui.themes import COLORS2, ColorKey
from datatools.tui.ansi import DOUBLE_UNDERLINE_BYTES
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

    def __init__(self, render_data: RenderData):
        self.render_data = render_data
        self.dictionary = render_data.column_metadata.dictionary
        self.title = render_data.column_presentation.title
        self.keyword = ...

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

        index = self.dictionary.get(value)
        for i in range(start, end):

            buffer += set_colors_cmd_bytes2(
                COLORS2[ColorKey.BOX_DRAWING][0],
                hash_to_rgb(hash_code(value), offset=64) if index is not None and index == i else COLORS2[ColorKey.BOX_DRAWING][1]
            )
            buffer += (LEFT_BORDER_BYTES if i == 0 else b' ')

        return buffer

    def focus_gained(self, line):
        self.keyword = self.render_data.named_cell_value_f(line, self.render_data.column_key)
        return True

    def focus_lost(self, line):
        self.keyword = ...
        return True

    def focus_moved(self, old_line, line):
        new_keyword = self.render_data.named_cell_value_f(line, self.render_data.column_key)
        self.keyword = new_keyword
        return True

    def __getitem__(self, row):
        return MASK_ROW_EMPHASIZED if self.render_data.named_cell_value_f(row, self.render_data.column_key) == self.keyword else 0
