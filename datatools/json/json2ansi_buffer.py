from datatools.util.table_util import *


class Buffer:
    width: int
    height: int
    chars: List[bytearray]  # every character is represented by 2 bytes (utf-16le)
    attrs: List[bytearray]  # for each character: 1 byte of attributes + 3 bytes for custom bg color (RGB)

    MASK_NONE = 0x00
    MASK_BOLD = 0x01
    MASK_ITALIC = 0x02
    MASK_FG_EMPHASIZED = 0x10
    MASK_BG_EMPHASIZED = 0x20
    MASK_BG_CUSTOM = 0x40
    MASK_OVERLINE = 0x80

    TAB_SIZE = 4

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.chars = [self.spaces(width) for _ in range(height)]
        self.attrs = [bytearray(4 * width) for _ in range(height)]

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

    def draw_text(self, x: int, y: int, text: str, mask: int = 0):
        _y = y
        _x = x
        char_line = self.chars[_y]
        char_i = 2 * _x
        attr_line = self.attrs[_y]
        attr_i = 4 * _x

        for c in text:
            if c == '\n':
                _x = x
                _y += 1
                char_line = self.chars[_y]
                char_i = 2 * _x
                attr_line = self.attrs[_y]
                attr_i = 4 * _x
            elif c == '\t':
                _x = x + (_x - x + Buffer.TAB_SIZE) // Buffer.TAB_SIZE * Buffer.TAB_SIZE
                char_i = 2 * _x
                attr_i = 4 * _x
            else:
                attr_line[attr_i] |= mask
                attr_i += 4

                code = ord(c)
                char_line[char_i] = code & 0xff
                char_i += 1
                char_line[char_i] = (code >> 8) & 0xff
                char_i += 1

                _x += 1

    def draw_attrs_box(self, x: int, y: int, width: int, height: int, mask: int):
        for j in range(height):
            line = self.attrs[y]
            for i in range(width):
                line[(x + i) * 4] |= mask
            y += 1

    def draw_bg_colors_box(self, x: int, y: int, width: int, height: int, r: int, g: int, b: int):
        for j in range(height):
            line = self.attrs[y]
            for i in range(width):
                line[(x + i) * 4 + 1] = r
                line[(x + i) * 4 + 2] = g
                line[(x + i) * 4 + 3] = b
            y += 1

    def flush(self, screen_width, screen_height):
        width = min(screen_width, self.width)
        height = min(screen_height, self.height)
        for y in range(height):
            print(self.to_string(0, y, width))

    def to_string(self, x, y, width):
        s = ''
        prev_attr = -1
        prev_r = -1
        prev_g = -1
        prev_b = -1

        for x in range(x, x + width):
            c = chr(self.chars[y][2 * x] + (self.chars[y][2 * x + 1] << 8))
            attr = self.attrs[y][4 * x]
            r = self.attrs[y][4 * x + 1]
            g = self.attrs[y][4 * x + 2]
            b = self.attrs[y][4 * x + 3]

            if attr != prev_attr or ((attr & Buffer.MASK_BG_CUSTOM) != 0 and (r != prev_r or g != prev_g or b != prev_b)):
                s += '\x1b[0;' + self.attr_to_ansi(attr, r, g, b) + 'm'
            s += c

            prev_attr = attr
            prev_r = r
            prev_g = g
            prev_b = b

        return s + '\x1b[0;m'   # (for the last line only)

    def attr_to_ansi(self, attr, r, g, b):
        codes = ['37']
        if attr & self.MASK_BOLD:
            codes.append('1')
        if attr & self.MASK_ITALIC:
            codes.append('3')

        if attr & self.MASK_BG_CUSTOM:
            codes.append('48;2')
            codes.append(str(r))
            codes.append(str(g))
            codes.append(str(b))
        elif attr & self.MASK_BG_EMPHASIZED:
            codes.append('48;5;237')
        else:
            codes.append('40')

        if attr & self.MASK_FG_EMPHASIZED:
            codes.append('97')
        if attr & self.MASK_OVERLINE:
            codes.append('53')
        return ';'.join(codes)
