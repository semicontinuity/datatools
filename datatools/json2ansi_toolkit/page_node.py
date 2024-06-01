from typing import Optional, List

from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.json2ansi_buffer import Buffer


class PageNode:
    def __init__(self, root: Block, title, background_color: Optional[List[int]] = None):
        self.root = root
        self.title = title
        self.background_color = background_color

    def layout(self):
        self.root.compute_width()
        self.root.compute_height()
        self.root.compute_position(0, 0)

    def paint(self) -> Buffer:
        self.layout()
        buffer = Buffer(self.root.width, self.root.height, self.background_color)
        self.root.paint(buffer)
        return buffer
