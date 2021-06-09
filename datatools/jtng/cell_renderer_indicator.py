from datatools.jt.themes import COLORS2, ColorKey
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES
from datatools.tui.terminal import set_colors_cmd_bytes2


class WIndicatorCellRenderer:
    def __len__(self):
        return 1

    def __call__(self, is_under_cursor, max_width, start, end, value):
        return set_colors_cmd_bytes2(
            COLORS2[ColorKey.BOX_DRAWING][0],
            COLORS2[ColorKey.TEXT][1] if value is None else COLORS2[ColorKey.TEXT][0]
        ) + LEFT_BORDER_BYTES

    def toggle(self):
        pass
