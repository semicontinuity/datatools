from datatools.jt.auto_metadata import ColumnMetadata
from datatools.jt.auto_presentation import ColumnPresentation
from datatools.jt.themes import COLORS2, ColorKey
from datatools.jtng.cell_renderer import WCellRenderer, DOUBLE_UNDERLINE_BYTES
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES
from datatools.tui.terminal import set_colors_cmd_bytes2


class WStripesCellRenderer(WCellRenderer):
    full_block = '\u2588'

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
                attrs = COLORS2[ColorKey.BOX_DRAWING]
                buffer += set_colors_cmd_bytes2(*attrs) + bytes(text[max(0, start - 1):end - 1], 'utf-8')
            if end == max_width:
                buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING]) + b' '

            return buffer
