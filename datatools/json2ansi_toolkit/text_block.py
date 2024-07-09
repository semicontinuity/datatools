from typing import AnyStr, Tuple

from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.json2ansi_buffer import Buffer
from datatools.util.text_util import geometry


class TextBlock(Block):
    def __init__(self, text: AnyStr, mask: int, bg: Tuple[int, int, int] = None):
        width, height = geometry(text)
        self.text = text
        self.mask = mask
        self.width = width
        self.height = height
        self.bg = bg

    def paint(self, buffer: Buffer):
        # background
        if self.mask != 0 or self.bg is not None:
            mask = self.mask if self.bg is None else self.mask | Buffer.MASK_BG_CUSTOM
            buffer.draw_attrs_box(self.x, self.y, self.width, self.height, mask)
            if self.bg is not None:
                buffer.draw_bg_colors_box(self.x, self.y, self.width, self.height, *self.bg)

        buffer.draw_text(self.x, self.y, self.text)
