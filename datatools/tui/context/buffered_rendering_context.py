from typing import Optional, List, Tuple, Union

from datatools.tui.context.rendering_context import RenderingContext


class BufferedRenderingContext(RenderingContext):
    width: int
    height: int
    chars: List[bytearray]  # every character is represented by 2 bytes (utf-16le)
    fg_attrs: List[bytearray]  # for each character: 1 byte of "public" attributes + 3 bytes for custom fg color (RGB)
    bg_attrs: List[bytearray]  # for each character: 1 byte of "private" attributes + 3 bytes for custom bg color (RGB)
    fg_color_default: Union[int, List[int]] = 7  # indexed color or RGB
    bg_color_default: Union[int, List[int]] = 0  # indexed color or RGB
    fg_color_emphasized: Union[int, List[int]] = 3  # indexed color or RGB (3=yellow; 250=bright gray?)
    bg_color_emphasized: Union[int, List[int]] = 237  # indexed color or RGB (dark gray)
    fg_color: Optional[List[int]] = None  # RGB only (extend to support indexed color)
    bg_color: Optional[List[int]] = None  # RGB only (extend to support indexed color)

    MASK_NONE = 0x00

    # BG attr byte
    MASK_FG_CUSTOM = 0x10
    MASK_BG_CUSTOM = 0x20
    MASK_CHANGED = 0x80

    TAB_SIZE = 4

    class Cursor:
        context: 'BufferedRenderingContext'
        x: int
        y: int
        char_i: int
        attr_i: int
        char_line: bytearray
        fg_attr_line: bytearray
        bg_attr_line: bytearray

        def __init__(self, context):
            self.context = context
            self.seek(0, 0)

        def seek(self, x: int, y: int):
            self.x = x
            self.y = y
            self.char_i = 2 * x
            self.attr_i = 4 * x
            self.char_line = self.context.chars[y]
            self.fg_attr_line = self.context.fg_attrs[y]
            self.bg_attr_line = self.context.bg_attrs[y]

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.chars = [self.spaces(width) for _ in range(height)]
        self.fg_attrs = [bytearray(4 * width) for _ in range(height)]
        self.bg_attrs = [bytearray(4 * width) for _ in range(height)]
        self.cursor = BufferedRenderingContext.Cursor(self)

    @staticmethod
    def spaces(width) -> bytearray:
        line = bytearray(2 * width)
        i = 0
        while i < width * 2:
            line[i] = 32
            i += 1
            line[i] = 0
            i += 1
        return line

    def __str__(self):
        # Reset attrs after each line, otherwise the line will be filled with BG color when terminal window scrolls
        return ''.join([self.row_slice_to_string(y, 0, self.width) + '\x1b[0m\n' for y in range(self.height)])

    def draw_attrs_box_at(self, box_x: int, box_y: int, box_width: int, box_height: int,
                          attrs: int = 0,
                          fg: Optional[Tuple[int, int, int]] = None,
                          bg: Optional[Tuple[int, int, int]] = None):
        for j in range(max(0, box_y), min(self.height, box_y + box_height)):
            fg_line = self.fg_attrs[j]
            bg_line = self.bg_attrs[j]
            for i in range(max(0, box_x), min(self.width, box_x + box_width)):
                fg_line[i * 4] = attrs
                if fg is not None:
                    bg_line[i * 4] = BufferedRenderingContext.MASK_FG_CUSTOM
                    fg_line[i * 4 + 1] = fg[0]
                    fg_line[i * 4 + 2] = fg[1]
                    fg_line[i * 4 + 3] = fg[2]
                if bg is not None:
                    bg_line[i * 4] = BufferedRenderingContext.MASK_BG_CUSTOM
                    bg_line[i * 4 + 1] = bg[0]
                    bg_line[i * 4 + 2] = bg[1]
                    bg_line[i * 4 + 3] = bg[2]
                # if i == box_x:
                #     bg_line[i * 4] |= BufferedRenderingContext.MASK_CHANGED

    def draw_text_at(self, from_x: int, from_y: int, text: str, attrs: int = 0) -> Tuple[int, int]:
        """
        Draws texts at the specified coordinates.
        Does not modify cursor position.
        :return: x, y coordinates of cursor position after the text; if y is off-limits, y is set to height
        """
        _x = from_x
        _y = from_y
        char_line = self.chars[_y]
        char_i = 2 * _x
        fg_attr_line = self.fg_attrs[_y]
        bg_attr_line = self.bg_attrs[_y]
        attr_i = 4 * _x

        for c in text:
            if c == '\n':
                _x = from_x
                _y += 1
                if _y >= self.height:
                    break
                if 0 <= _y:
                    char_line = self.chars[_y]
                    char_i = 2 * _x
                    fg_attr_line = self.fg_attrs[_y]
                    bg_attr_line = self.bg_attrs[_y]
                    attr_i = 4 * _x
            elif c == '\t':
                to_x = from_x + (_x - from_x + BufferedRenderingContext.TAB_SIZE) // BufferedRenderingContext.TAB_SIZE * BufferedRenderingContext.TAB_SIZE
                while _x < to_x:
                    if 0 <= _y < self.height and 0 <= _x < self.width:
                        priv_attrs = bg_attr_line[attr_i]
                        if self.fg_color:
                            priv_attrs |= BufferedRenderingContext.MASK_FG_CUSTOM
                            bg_attr_line[attr_i] = priv_attrs
                            fg_attr_line[attr_i + 1] = self.fg_color[0]
                            fg_attr_line[attr_i + 2] = self.fg_color[1]
                            fg_attr_line[attr_i + 3] = self.fg_color[2]
                        if self.bg_color:
                            priv_attrs |= BufferedRenderingContext.MASK_BG_CUSTOM
                            bg_attr_line[attr_i + 1] = self.bg_color[0]
                            bg_attr_line[attr_i + 2] = self.bg_color[1]
                            bg_attr_line[attr_i + 3] = self.bg_color[2]

                        fg_attr_line[attr_i] |= attrs
                        bg_attr_line[attr_i] = priv_attrs
                        attr_i += 4

                        char_line[char_i] = 0x20    # lo(space)
                        char_i += 1
                        char_line[char_i] = 0x00    # hi(space)
                        char_i += 1

                    _x += 1
            else:
                if 0 <= _y < self.height and 0 <= _x < self.width:
                    priv_attrs = bg_attr_line[attr_i]
                    if self.fg_color:
                        priv_attrs |= BufferedRenderingContext.MASK_FG_CUSTOM
                        fg_attr_line[attr_i + 1] = self.fg_color[0]
                        fg_attr_line[attr_i + 2] = self.fg_color[1]
                        fg_attr_line[attr_i + 3] = self.fg_color[2]
                    if self.bg_color:
                        priv_attrs |= BufferedRenderingContext.MASK_BG_CUSTOM
                        bg_attr_line[attr_i + 1] = self.bg_color[0]
                        bg_attr_line[attr_i + 2] = self.bg_color[1]
                        bg_attr_line[attr_i + 3] = self.bg_color[2]

                    fg_attr_line[attr_i] |= attrs
                    bg_attr_line[attr_i] = priv_attrs
                    attr_i += 4

                    code = ord(c)
                    char_line[char_i] = code & 0xff
                    char_i += 1
                    char_line[char_i] = (code >> 8) & 0xff
                    char_i += 1

                _x += 1

        return _x, _y

    def row_slice_to_string(self, y, x_from, x_to):
        """ Coordinates must be valid """
        s = ''
        prev_attr = 0
        prev_priv_attr = 0

        prev_bg_r = None
        prev_bg_g = None
        prev_bg_b = None

        prev_fg_r = None
        prev_fg_g = None
        prev_fg_b = None

        for x in range(x_from, x_to):
            c = chr(self.chars[y][2 * x] + (self.chars[y][2 * x + 1] << 8))

            attr = self.fg_attrs[y][4 * x]
            fg_r = self.fg_attrs[y][4 * x + 1]
            fg_g = self.fg_attrs[y][4 * x + 2]
            fg_b = self.fg_attrs[y][4 * x + 3]

            priv_attr = self.bg_attrs[y][4 * x]
            bg_r = self.bg_attrs[y][4 * x + 1]
            bg_g = self.bg_attrs[y][4 * x + 2]
            bg_b = self.bg_attrs[y][4 * x + 3]

            attr_diff = (BufferedRenderingContext.MASK_FG_CUSTOM | BufferedRenderingContext.MASK_BG_CUSTOM) if x == x_from else attr ^ prev_attr
            priv_attr_diff = (RenderingContext.MASK_FG_EMPHASIZED | RenderingContext.MASK_BG_EMPHASIZED) if x == x_from else priv_attr ^ prev_priv_attr

            if not attr_diff and not priv_attr_diff:
                fg_changed = (priv_attr & BufferedRenderingContext.MASK_FG_CUSTOM) != 0 and (prev_fg_r != fg_r or prev_fg_g != fg_g or prev_fg_b != fg_b)
                bg_changed = (priv_attr & BufferedRenderingContext.MASK_BG_CUSTOM) != 0 and (prev_bg_r != bg_r or prev_bg_g != bg_g or prev_bg_b != bg_b)
                if bg_changed:
                    priv_attr_diff |= BufferedRenderingContext.MASK_BG_CUSTOM
                if fg_changed:
                    priv_attr_diff |= BufferedRenderingContext.MASK_FG_CUSTOM
            if attr_diff or priv_attr_diff:
                codes = self.attr_to_ansi(attr, attr_diff, priv_attr, priv_attr_diff, fg_r, fg_g, fg_b, bg_r, bg_g, bg_b)
                if codes != '':
                    s += '\x1b[' + codes + 'm'

            s += c

            prev_attr = attr
            prev_priv_attr = priv_attr

            prev_bg_r = bg_r
            prev_bg_g = bg_g
            prev_bg_b = bg_b

            prev_fg_r = fg_r
            prev_fg_g = fg_g
            prev_fg_b = fg_b

        return s

    def attr_to_ansi(self, attr: int, attr_diff: int, priv_attr: int, priv_attr_diff: int, fg_r, fg_g, fg_b, bg_r, bg_g, bg_b):
        codes: List[str] = []

        # ESC[x8;2;{r};{g};{b}m Set color as RGB.
        def append_rgb_color(code, r, g, b):
            codes.append(code)
            codes.append('2')
            codes.append(str(r))
            codes.append(str(g))
            codes.append(str(b))

        def append_fg_rgb_color(r, g, b):
            append_rgb_color('38', r, g, b)

        def append_bg_rgb_color(r, g, b):
            append_rgb_color('48', r, g, b)

        def append_fg_indexed_color(color: int):
            codes.append('38;5')
            codes.append(str(color))

        def append_bg_indexed_color(color: int):
            codes.append('48;5')
            codes.append(str(color))

        def append_fg_color(color):
            if type(color) is int:
                append_fg_indexed_color(color)
            else:
                append_fg_rgb_color(*color)

        def append_bg_color(color):
            if type(color) is int:
                append_bg_indexed_color(color)
            else:
                append_bg_rgb_color(*color)

        def maybe_adjust_bg_color():
            custom_bg_changed = priv_attr_diff & self.MASK_BG_CUSTOM
            custom_bg = priv_attr & self.MASK_BG_CUSTOM
            if custom_bg_changed and custom_bg:
                append_bg_rgb_color(bg_r, bg_g, bg_b)
                return

            emphasized_bg_changed = attr_diff & self.MASK_BG_EMPHASIZED
            emphasized_bg = attr & self.MASK_BG_EMPHASIZED
            if (custom_bg_changed or emphasized_bg_changed) and emphasized_bg and not custom_bg:
                append_bg_color(self.bg_color_emphasized)
                return

            if (custom_bg_changed or emphasized_bg_changed) and not custom_bg and not emphasized_bg:
                append_bg_color(self.bg_color_default)

        def maybe_adjust_fg_color():
            custom_fg_changed = priv_attr_diff & self.MASK_FG_CUSTOM
            custom_fg = priv_attr & self.MASK_FG_CUSTOM
            if custom_fg_changed and custom_fg:
                append_fg_rgb_color(fg_r, fg_g, fg_b)
                return

            emphasized_fg_changed = attr_diff & self.MASK_FG_EMPHASIZED
            emphasized_fg = attr & self.MASK_FG_EMPHASIZED
            if (custom_fg_changed or emphasized_fg_changed) and emphasized_fg and not custom_fg:
                append_fg_color(self.fg_color_emphasized)
                return

            if (custom_fg_changed or emphasized_fg_changed) and not custom_fg and not emphasized_fg:
                append_fg_color(self.fg_color_default)

        if attr_diff & self.MASK_BOLD:
            codes.append('1' if (attr & self.MASK_BOLD) else '22')
        if attr_diff & self.MASK_ITALIC:
            codes.append('3' if (attr & self.MASK_ITALIC) else '23')
        if attr_diff & self.MASK_OVERLINE:
            codes.append('53' if (attr & self.MASK_OVERLINE) else '55')

        maybe_adjust_bg_color()
        maybe_adjust_fg_color()

        return ';'.join(codes)
