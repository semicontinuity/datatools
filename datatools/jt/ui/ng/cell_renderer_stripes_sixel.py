from datatools.jt.model.presentation import ColumnRenderer
from datatools.jt.ui.cell_renderer import WColumnRenderer
from datatools.jt.ui.ng.render_data import RenderData
from datatools.jt.ui.themes import COLORS2, ColorKey
from datatools.tui.box_drawing_chars import LEFT_BORDER_BYTES
from datatools.tui.picotui_util import cursor_forward_cmd, cursor_up_cmd
from datatools.tui.sixel import sixel_append_set_color_register_cmd, sixel_append_start_cmd, sixel_append_stop_cmd, \
    sixel_append_use_color, sixel_append_repeated, sixel_append_lf
from datatools.tui.terminal import set_colors_cmd_bytes2


class WStripesSixelCellRenderer(WColumnRenderer):
    SIXELS_PER_CHAR: int = 10   # characters are assumed to be 20x10 by sixel-compatible terminals
    SIXELS_PER_STRIPE: int = 2   # characters are assumed to be 20x10 by sixel-compatible terminals
    STRIPES_PER_CHAR = SIXELS_PER_CHAR // SIXELS_PER_STRIPE

    def __init__(
            self,
            column_renderer: ColumnRenderer,
            render_data: RenderData):

        self.max_content_width = column_renderer.max_content_width
        self.render_data = render_data

    def toggle(self):
        self.render_data.column_state.collapsed = not self.render_data.column_state.collapsed

    def to_color_list(self, value):
        return []

    def __len__(self):
        return 1 if self.render_data.column_state.collapsed else self.max_content_width
        # return 1 if self.state.collapsed else self.chars_required_for_stripes(self.max_content_width) + 2

    def __call__(self, attrs, column_width, start, end, value, row):
        if self.render_data.column_state.collapsed:
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
            if start < column_width - 1 and end > 1:
                # Paint with default terminal background
                # This is for Gnome Terminal, which ignores currently set BG color, and uses terminal default BG color
                buffer += b'\x1b[49m'    # reset to default BG color

                chars_from = 0 if start == 0 else start - 1
                chars_to = column_width - 2 if end == column_width else end - 1

                to = min(chars_to, self.chars_required_for_stripes(length))
                painted_chars = self.append_stripes(colors, chars_from * self.STRIPES_PER_CHAR, to * self.STRIPES_PER_CHAR, buffer)
                buffer += cursor_up_cmd(1)  # restore cursor pos, because *$* terminal moves cursor to the next line

                if painted_chars > 0:
                    buffer += cursor_forward_cmd(painted_chars)  # skip stripes
                if painted_chars < chars_to:
                    buffer += b' ' * (chars_to - max(chars_from, painted_chars))
            if end == column_width:
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
                sixel_append_repeated(buffer, self.SIXELS_PER_STRIPE, bits)
            sixel_append_lf(buffer)
            bits = 0b00111111   # all 6 pixels painted

        payload_sixels = (end_stripe - start_stripe) * self.SIXELS_PER_STRIPE
        if payload_sixels > 0:
            width_sixels = self.chars_required_for_sixels(payload_sixels) * self.SIXELS_PER_CHAR
            remaining_sixels = payload_sixels - width_sixels
            if remaining_sixels > 0:
                sixel_append_repeated(buffer, remaining_sixels, 0)
                payload_sixels += remaining_sixels

        sixel_append_stop_cmd(buffer)
        return payload_sixels // self.SIXELS_PER_CHAR

    @staticmethod
    def stripes_for_chars(chars):
        return WStripesSixelCellRenderer.STRIPES_PER_CHAR * chars

    @staticmethod
    def chars_required_for_stripes(stripes):
        return (stripes + WStripesSixelCellRenderer.STRIPES_PER_CHAR - 1) // WStripesSixelCellRenderer.STRIPES_PER_CHAR

    @staticmethod
    def chars_required_for_sixels(sixels):
        return (sixels + WStripesSixelCellRenderer.SIXELS_PER_CHAR - 1) // WStripesSixelCellRenderer.SIXELS_PER_CHAR
