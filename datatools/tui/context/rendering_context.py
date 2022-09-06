from typing import Optional, List, Tuple, Union


class RenderingContext:
    MASK_NONE = 0x00

    MASK_BOLD = 0x01
    MASK_ITALIC = 0x02
    MASK_FG_EMPHASIZED = 0x10
    MASK_BG_EMPHASIZED = 0x20
    MASK_OVERLINE = 0x80

    x: int = 0
    y: int = 0

    def draw_attrs_box_at(self, x: int, y: int, width: int, height: int, attrs: int,
                       fg: Optional[Tuple[int, int, int]] = None,
                       bg: Optional[Tuple[int, int, int]] = None):
        pass

    def draw_text_at(self, from_x: int, from_y: int, text: str, attrs: int = 0) -> Tuple[int, int]:
        """
        Draws texts at the specified coordinates.
        Does not modify cursor position.
        :param attrs: additional attributes to be applied
        :return: x, y coordinates of cursor position right after the text; if y is off-limits, y is set to height.
        """
        pass

    def draw_text(self, text: str, attrs: int = 0):
        """
        Draws texts at the current cursor position.
        Modifies cursor position.
        :param attrs: additional attributes to be applied
        """
        self.x, self.y = self.draw_text_at(self.x, self.y, text, attrs)
