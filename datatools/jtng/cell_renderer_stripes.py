from datatools.jt.auto_metadata import ColumnMetadata
from datatools.jt.auto_presentation import ColumnPresentation
from datatools.jt.themes import COLORS2, ColorKey
from datatools.jtng.cell_renderer import WCellRenderer, DOUBLE_UNDERLINE_BYTES
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES, FULL_BLOCK_BYTES
from datatools.tui.coloring import hash_to_rgb
from datatools.tui.terminal import set_colors_cmd_bytes2


class WStripesCellRenderer(WCellRenderer):

    def __init__(self, column_metadata: ColumnMetadata, column_presentation: ColumnPresentation, max_content_width, column_state):
        self.max_content_width = max_content_width
        self.column_metadata = column_metadata
        self.column_presentation = column_presentation
        self.state = column_state

    def __len__(self):
        return 2 + self.max_content_width

    def __call__(self, is_under_cursor, max_width, start, end, value, assistant_value):
        if self.state.collapsed:
            cell_attrs = COLORS2[ColorKey.BOX_DRAWING]
            return set_colors_cmd_bytes2(
                COLORS2[ColorKey.BOX_DRAWING][0],
                cell_attrs[0]
            ) + LEFT_BORDER_BYTES
        else:
            stripes = [] if value is None or len(value) == 0 else [int(s, 16) for s in value.split(',')]
            length = len(stripes)

            buffer = bytearray()
            if is_under_cursor:
                buffer += DOUBLE_UNDERLINE_BYTES

            if start == 0:
                buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING]) + LEFT_BORDER_BYTES
            if start < max_width - 1 and end > 1:
                index_from = 0 if start == 0 else start - 1
                index_to = max_width - 2 if end == max_width else end - 1
                WStripesCellRenderer.append_stripes(stripes, index_from, min(index_to, length), buffer)
                buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING])
                buffer += b' ' * (index_to - length)
            if end == max_width:
                buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING]) + b' '
                buffer += b' '

            return buffer

    @staticmethod
    def append_stripes(list_of_hash_codes, start, end, buffer):
        for i in range(start, end):
            hash_code = list_of_hash_codes[i]
            color = hash_to_rgb(hash_code, offset=64)
            buffer += set_colors_cmd_bytes2(color)
            buffer += FULL_BLOCK_BYTES
