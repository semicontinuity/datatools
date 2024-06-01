from typing import AnyStr, Tuple

from datatools.json2ansi_toolkit.border_style import BorderStyle
from datatools.tui.box_drawing_chars import LEFT_BORDER
from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.json2ansi_buffer import Buffer
from datatools.util.text_util import geometry


class TextCell(Block):
    def __init__(self, text: AnyStr, mask: int, border_style: BorderStyle, bg: Tuple[int, int, int] = None):
        width, height = geometry(text)
        self.text = text
        self.mask = mask
        self.width = width + 2
        self.height = height
        self.bg = bg
        self.border_style = border_style

    def paint(self, buffer: Buffer):
        # background
        if self.mask != 0 or self.bg is not None:
            mask = self.mask if self.bg is None else self.mask | Buffer.MASK_BG_CUSTOM
            buffer.draw_attrs_box(self.x, self.y, self.width, self.height, mask)
            if self.bg is not None:
                buffer.draw_bg_colors_box(self.x, self.y, self.width, self.height, *self.bg)

        # TODO: if border is off, visual artifacts appear - Table node should paint its grid
        # top border
        if self.border_style.top:
            buffer.draw_attrs_box(self.x, self.y, self.width, 1, Buffer.MASK_OVERLINE)

        # left border
        for j in range(self.height):
            buffer.draw_text(self.x, self.y + j, LEFT_BORDER)

        buffer.draw_text(self.x + 1, self.y, self.text)
