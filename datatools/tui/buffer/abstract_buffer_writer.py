from typing import Optional, List


class AbstractBufferWriter:
    x: int
    y: int
    fg_color: Optional[List[int]] = None  # RGB only (extend to support indexed color)
    bg_color: Optional[List[int]] = None  # RGB only (extend to support indexed color)

    TAB_SIZE = 4

    MASK_NONE = 0x00

    MASK_BOLD = 0x01
    MASK_ITALIC = 0x02
    MASK_UNDERLINED = 0x04
    MASK_CROSSED_OUT = 0x08
    MASK_FG_EMPHASIZED = 0x10
    MASK_BG_EMPHASIZED = 0x20
    MASK_OVERLINE = 0x80

    def go_to(self, x: int, y: int):
        self.x = x
        self.y = y

    def cr_lf(self, x: int):
        self.go_to(x, self.y + 1)

    def put_char(self, c: str, attrs: int):
        pass

    def draw_attrs_box(self, box_width: int, box_height: int, attrs: int = 0):
        pass

    def draw_text(self, text: str, attrs: int = 0):
        """
        Draws texts at the current cursor position.
        Modifies cursor position.
        :param text: multi-line text to draw (can contain '\n' and '\t')
        :param attrs: additional attributes to be applied
        """
        from_x = self.x

        for c in text:
            if c == '\n':
                self.cr_lf(from_x)
            elif c == '\t':
                _x = self.x
                to_x = from_x + (
                        _x - from_x + self.TAB_SIZE) // self.TAB_SIZE * self.TAB_SIZE
                for i in range(_x, to_x):
                    self.put_char(' ', attrs)
            else:
                self.put_char(c, attrs)
