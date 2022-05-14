from datatools.jt.model.metadata import ColumnMetadata
from datatools.jt.model.presentation import ColumnPresentation
from datatools.jt.ui.themes import COLORS2, ColorKey
from datatools.jt.model.attributes import MASK_ROW_CURSOR
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.tui.ansi import DOUBLE_UNDERLINE_BYTES
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES, FULL_BLOCK_BYTES
from datatools.tui.coloring import hash_to_rgb
from datatools.tui.terminal import set_colors_cmd_bytes2


class WStripesCellRenderer(WColumnRenderer):

    def __init__(self, column_metadata: ColumnMetadata, column_presentation: ColumnPresentation, max_content_width, column_state):
        self.max_content_width = max_content_width
        self.column_metadata = column_metadata
        self.column_presentation = column_presentation
        self.state = column_state

    def toggle(self):
        self.state.collapsed = not self.state.collapsed

    def __len__(self):
        return 1 if self.state.collapsed else self.max_content_width + 2

    def __call__(self, row_attrs, column_width, start, end, value, assistant_value, row):
        if self.state.collapsed:
            # distinguish only empty
            cell_attrs = (COLORS2[ColorKey.BOX_DRAWING][1], None) if value is None or len(value) == 0 else COLORS2[ColorKey.TEXT]
            return set_colors_cmd_bytes2(COLORS2[ColorKey.BOX_DRAWING][0], cell_attrs[0]) + LEFT_BORDER_BYTES
        else:
            if value is None or len(value) == 0:
                stripes = []
            elif type(value) is list:
                stripes = [int(s, 16) for s in value]
            else:
                stripes = [int(s, 16) for s in value.split(',')]
            length = len(stripes)

            buffer = bytearray()
            if row_attrs & MASK_ROW_CURSOR:
                buffer += DOUBLE_UNDERLINE_BYTES

            if start == 0:
                buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING]) + LEFT_BORDER_BYTES
            if start < column_width - 1 and end > 1:
                index_from = 0 if start == 0 else start - 1
                index_to = column_width - 2 if end == column_width else end - 1
                to = min(index_to, length)
                WStripesCellRenderer.append_stripes(stripes, index_from, to, buffer)
                if to < index_to:
                    buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING])
                    buffer += b' ' * (index_to - max(index_from, to))
            if end == column_width:
                buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING])
                buffer += b' '

            return buffer

    @staticmethod
    def append_stripes(list_of_hash_codes, start, end, buffer):
        for i in range(start, end):
            hash_code = list_of_hash_codes[i]
            color = hash_to_rgb(hash_code, offset=64)
            buffer += set_colors_cmd_bytes2(color)
            buffer += FULL_BLOCK_BYTES
