from typing import List

from datatools.json2ansi_toolkit.border_style import BorderStyle
from datatools.json2ansi_toolkit.text_cell import TextCell
from datatools.tui.buffer.json2ansi_buffer import Buffer


class HeaderNode(TextCell):
    def __init__(self, key, is_uniform, border_style: BorderStyle):
        super().__init__(str(key), self.attr_for(is_uniform), border_style)

    # TODO
    def compute_widths(self) -> List[int]:
        self.compute_width()
        return [self.width]

    # TODO
    def set_min_widths(self, sizes: List[int]):
        pass

    @staticmethod
    def attr_for(is_uniform):
        if is_uniform:
            return Buffer.MASK_FG_EMPHASIZED | Buffer.MASK_BG_EMPHASIZED | Buffer.MASK_BOLD
        else:
            return Buffer.MASK_FG_EMPHASIZED | Buffer.MASK_BG_EMPHASIZED
