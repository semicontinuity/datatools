from datatools.jt.auto_metadata import ColumnMetadata
from datatools.jt.auto_presentation import ColumnPresentation
from datatools.jt.themes import COLORS2, ColorKey
from datatools.jtng.cell_renderer import WCellRenderer
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES
from datatools.tui.picotui_util import cursor_forward_cmd, cursor_up_cmd
from datatools.tui.sixel import sixel_append_set_color_register_cmd, sixel_append_start_cmd, sixel_append_stop_cmd, \
    sixel_append_use_color, sixel_append_repeated, sixel_append_lf
from datatools.tui.terminal import set_colors_cmd_bytes2


class WStripesSixelCellRenderer(WCellRenderer):
    SIXELS_PER_CHAR: int = 10   # characters are assumed to be 20x10 by sixel-compatible terminals

    def __init__(self, column_metadata: ColumnMetadata, column_presentation: ColumnPresentation, max_content_width, column_state):
        self.max_content_width = max_content_width
        self.column_metadata = column_metadata
        self.column_presentation = column_presentation
        self.state = column_state
        self.sixels_per_stripe = 2
        self.stripes_per_char = self.SIXELS_PER_CHAR // self.sixels_per_stripe

    def toggle(self):
        self.state.collapsed = not self.state.collapsed

    def to_color_list(self, value):
        return []

    def __len__(self):
        return 1 if self.state.collapsed else self.chars_required_for_stripes(self.max_content_width) + 2

    def __call__(self, is_under_cursor, max_width, start, end, value, assistant_value):
        if self.state.collapsed:
            # distinguish only empty
            cell_attrs = (COLORS2[ColorKey.BOX_DRAWING][1], None) if value is None or len(value) == 0 else COLORS2[ColorKey.TEXT]
            return set_colors_cmd_bytes2(COLORS2[ColorKey.BOX_DRAWING][0], cell_attrs[0]) + LEFT_BORDER_BYTES
        else:
            colors = self.to_color_list(value)
            length = len(colors)

            buffer = bytearray()

            if start == 0:
                buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING])
                buffer += LEFT_BORDER_BYTES
            if start < max_width - 1 and end > 1:
                # Paint with default terminal background
                # This is for Gnome Terminal, which ignores currently set BG color, and uses terminal default BG color
                buffer += b'\x1b[49m'    # reset to default BG color

                index_from = 0 if start == 0 else start - 1
                index_to = max_width - 2 if end == max_width else end - 1

                to = min(index_to, self.chars_required_for_stripes(length))
                painted_chars = self.append_stripes(colors, index_from * self.stripes_per_char, to * self.stripes_per_char, buffer)
                buffer += cursor_up_cmd(1)  # restore cursor pos, because *$* terminal moves cursor to the next line

                if painted_chars > 0:
                    buffer += cursor_forward_cmd(painted_chars)  # skip stripes
                if painted_chars < index_to:
                    buffer += b' ' * (index_to - max(index_from, painted_chars))
            if end == max_width:
                buffer += set_colors_cmd_bytes2(*COLORS2[ColorKey.BOX_DRAWING])
                buffer += b' '

            return buffer

    def append_stripes(self, list_of_colors, start_stripe, end_stripe, buffer):
        color_index = 0
        color_indices = {}

        sixel_append_start_cmd(buffer)

        for i in range(start_stripe, end_stripe):
            if i >= len(list_of_colors):
                break
            color = list_of_colors[i]
            index = color_indices.get(color)
            if index is None:
                color_indices[color] = color_index
                sixel_append_set_color_register_cmd(
                    buffer, color_index, color[0] * 99 // 255, color[1] * 99 // 255, color[2] * 99 // 255)
                color_index += 1

        # "Standard" sixels assume that characters are 10x20 "pixels".
        # 3 "swim lanes" of sixels occupy 3*6 = 18 "pixels", painting 4th "swim lane" will touch the next row.
        # Thus, only 3 "swim lanes are utilized + 2 "pixels" at the bottom are not painted.
        # For symmetry, 2 top pixels are also not painted, and the actual stripe geometry is:
        # 2 background pixels at the top + 16 pixels at the center + 2 background pixels at the bottom.
        bits = 0b00111100   # 2 pixel at the top not painted + 4 pixels of the stripe
        for j in range(3):
            color_index = -1
            for i in range(start_stripe, end_stripe):
                if i >= len(list_of_colors):
                    break
                color = list_of_colors[i]
                index = color_indices.get(color)
                if index != color_index:
                    sixel_append_use_color(buffer, index)
                    color_index = index
                sixel_append_repeated(buffer, self.sixels_per_stripe, bits)
            sixel_append_lf(buffer)
            bits = 0b00111111   # all 6 pixels painted

        payload_sixels = (end_stripe - start_stripe) * self.sixels_per_stripe
        if payload_sixels > 0:
            width_sixels = self.chars_required_for_sixels(payload_sixels) * self.SIXELS_PER_CHAR
            remaining_sixels = payload_sixels - width_sixels
            if remaining_sixels > 0:
                sixel_append_repeated(buffer, remaining_sixels, 0)
                payload_sixels += remaining_sixels

        sixel_append_stop_cmd(buffer)
        return payload_sixels // self.SIXELS_PER_CHAR

    def chars_required_for_stripes(self, stripes):
        return (stripes + self.stripes_per_char - 1) // self.stripes_per_char

    def chars_required_for_sixels(self, sixels):
        return (sixels + self.SIXELS_PER_CHAR - 1) // self.SIXELS_PER_CHAR
