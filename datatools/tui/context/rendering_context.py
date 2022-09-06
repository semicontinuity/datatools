from typing import Optional, List, Tuple, Union


class RenderingContext:
    MASK_NONE = 0x00

    MASK_BOLD = 0x01
    MASK_ITALIC = 0x02
    MASK_FG_EMPHASIZED = 0x10
    MASK_BG_EMPHASIZED = 0x20
    MASK_OVERLINE = 0x80

    def draw_attrs_box_at(self, x: int, y: int, width: int, height: int, attrs: int,
                       fg: Optional[Tuple[int, int, int]] = None,
                       bg: Optional[Tuple[int, int, int]] = None):
        pass

    def draw_text(self, text: str, attrs: int = 0):
        """
        Draws texts at the current cursor position.
        Modifies cursor position.
        :param text: multi-line text to draw (can contain '\n' and '\t')
        :param attrs: additional attributes to be applied
        """
        pass
