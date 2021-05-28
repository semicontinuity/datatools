from datatools.util.table_util import *


class Buffer:
    width: int
    height: int
    chars: List[bytearray]  # every characters is represented by 2 bytes (utf-16le)
    attrs: List[bytearray]

    MASK_NONE = 0x00
    MASK_BOLD = 0x01
    MASK_ITALIC = 0x02
    MASK_FG_EMPHASIZED = 0x10
    MASK_BG_EMPHASIZED = 0x20
    MASK_OVERLINE = 0x80

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.chars = [self.spaces(width) for _ in range(height)]
        self.attrs = [bytearray(width) for _ in range(height)]

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
        attr_line = self.attrs[y]
        char_line = self.chars[y]
        char_i = 2 * x
        for c in text:
            attr_line[x] |= mask
            x += 1

            code = ord(c)
            char_line[char_i] = code & 0xff
            char_i += 1
            char_line[char_i] = (code >> 8) & 0xff
            char_i += 1

    def draw_attrs_box(self, x: int, y: int, width: int, height: int, mask: int):
        for j in range(height):
            line = self.attrs[y]
            for i in range(width):
                line[x + i] |= mask
            y += 1

    def draw_mask(self, x: int, y: int, width: int, mask: int):
        line = self.attrs[y]
        for _ in range(width):
            line[x] |= mask
            x += 1

    def flush(self, screen_width, screen_height):
        width = min(screen_width, self.width)
        height = min(screen_height, self.height)
        for y in range(height):
            s = ''
            for x in range(width):
                c = chr(self.chars[y][2 * x] + (self.chars[y][2 * x + 1] << 8))
                attr = self.attrs[y][x]
                s += self.attr_to_ansi(attr) + c + '\x1b[0m'
            print(s)

    def attr_to_ansi(self, attr):
        codes = []
        if attr & self.MASK_BOLD:
            codes.append('1')
        if attr & self.MASK_ITALIC:
            codes.append('3')
        if attr & self.MASK_BG_EMPHASIZED:
            codes.append('48;5;237')
        else:
            codes.append('40')
        if attr & self.MASK_FG_EMPHASIZED:
            codes.append('97')
        if attr & self.MASK_OVERLINE:
            codes.append('53')
        return '\x1b[' + ';'.join(codes) + 'm'
