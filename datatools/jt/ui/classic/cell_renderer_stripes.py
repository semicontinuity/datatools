from datatools.jt.ui.themes import COLORS, ColorKey
from datatools.tui.box_drawing_chars import FULL_BLOCK
from datatools.tui.coloring import decode_rgb
from datatools.tui.terminal import ansi_foreground_escape_code, set_colors_cmd_bytes


class WStripesCellRenderer:
    def __init__(self, column_spec):
        self.column_spec = column_spec

    def __call__(self, row_attrs, max_width, start, end, value):
        if value is None:
            value = []
        length = len(value)
        value = value[start:end]
        text = self.stripes(value, self.column_spec)
        attrs = COLORS[ColorKey.TEXT]
        return set_colors_cmd_bytes(*attrs) + bytes(text, 'utf-8') + b' ' * (max_width - length)

    @staticmethod
    def stripes(cell_contents, column_spec):
        spec_list = list(column_spec.items())
        if len(spec_list) == 1 and type(spec_list[0][1]) is dict:
            return WStripesCellRenderer.stripes_for_nested_spec(cell_contents, spec_list[0][0], spec_list[0][1])
        else:
            return WStripesCellRenderer.stripes_for_plain_spec(cell_contents, column_spec)

    @staticmethod
    def stripes_for_plain_spec(cell_contents, column_spec):
        s = ""
        for cell in cell_contents:
            rgb_string = column_spec.get(cell)
            attr = ansi_foreground_escape_code(*decode_rgb(rgb_string) if rgb_string is not None else (255, 255, 255))
            s = s + attr + FULL_BLOCK
        return s

    @staticmethod
    def stripes_for_nested_spec(cell_contents, field, spec):
        s = ""
        for cell in cell_contents:
            rgb_string = spec.get(cell[field])
            attr = ansi_foreground_escape_code(*decode_rgb(rgb_string) if rgb_string is not None else (255, 255, 255))
            s = s + attr + FULL_BLOCK
        return s
