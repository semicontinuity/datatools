from dataclasses import dataclass
from typing import Dict

from datatools.jt.model.attributes import MASK_ROW_CURSOR
from datatools.jt.model.column_state import ColumnState
from datatools.jt.model.metadata import ColumnMetadata
from datatools.jt.model.presentation import ColumnPresentation, ColumnRenderer
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.themes import COLORS2, ColorKey
from datatools.tui.ansi import DOUBLE_UNDERLINE_BYTES
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES, LEFT_BORDER
from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.tui.terminal import set_colors_cmd_bytes2


@dataclass
class ColumnRendererDictIndexHashColored(ColumnRenderer):
    type = 'dict-index-hash-colored'

    def make_delegate(self, column_metadata: ColumnMetadata, column_presentation: 'ColumnPresentation', column_state: ColumnState):
        return WDictIndexCellRenderer(column_metadata, column_presentation)


class WDictIndexCellRenderer(WColumnRenderer):
    dictionary: Dict[str, int]

    def __init__(self, column_metadata: ColumnMetadata, column_presentation: ColumnPresentation):
        self.dictionary = column_metadata.dictionary
        self.title = column_presentation.title

    def __str__(self):
        if len(self.title) < len(self.dictionary) + 1:
            return LEFT_BORDER
        else:
            return LEFT_BORDER + self.title

    def __len__(self):
        return len(self.dictionary)

    def __call__(self, row_attrs, max_width, start, end, value, assistant_value):
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
