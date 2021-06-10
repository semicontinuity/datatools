from datatools.jt.themes import COLORS2, ColorKey
from datatools.jtng.cell_renderer import DOUBLE_UNDERLINE_BYTES, WCellRenderer
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES
from datatools.tui.terminal import set_colors_cmd_bytes2


class WIndicatorCellRenderer(WCellRenderer):
    def __len__(self):
        return 1

    def __call__(self, is_under_cursor, max_width, start, end, value, assistant_value):
        buffer = bytearray()
        if is_under_cursor:
            buffer += DOUBLE_UNDERLINE_BYTES
        buffer += set_colors_cmd_bytes2(
            COLORS2[ColorKey.BOX_DRAWING][0],
            COLORS2[ColorKey.TEXT][0] if value is not None else COLORS2[ColorKey.BOX_DRAWING][1]
        )
        buffer += LEFT_BORDER_BYTES
        return buffer
