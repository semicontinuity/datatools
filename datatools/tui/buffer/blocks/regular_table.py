from typing import List

from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.blocks.hbox import HBox


class RegularTable(Block):
    contents: List[HBox] = []

    def __init__(self, contents=None):
        self.contents = [] if contents is None else contents
        self.width = 0
        self.height = 0

    # overrides method from parent
    def compute_width(self):
        widths = self.compute_widths()

        for row in self.contents:
            for i in range(len(row.contents)):
                row.contents[i].width = widths[i]

        self.width = sum(width for width in widths)

    # overrides method from parent
    def compute_widths(self):
        widths = [0] * max((len(row.contents) for row in self.contents), default=0)
        for row in self.contents:
            row.compute_width()
        for row in self.contents:
            for i in range(len(row.contents)):
                widths[i] = max(widths[i], row.contents[i].width)
        return widths

    # overrides method from parent
    def compute_height(self):
        self.height = sum(size for size in self.compute_heights())

    # overrides method from parent
    def compute_heights(self):
        for row in self.contents:
            row.compute_height()
        return [child.height for child in self.contents]

    # overrides method from parent
    def set_min_widths(self, sizes: List[int]):
        for row in self.contents:
            for i in range(len(row.contents)):
                row.contents[i].width = max(row.contents[i].width, sizes[i])

    # overrides method from parent
    def set_min_heights(self, sizes: List[int]):
        for i in range(len(sizes)):
            self.contents[i].height = max(self.contents[i].height, sizes[i])

    # overrides method from parent
    def compute_position(self, parent_x: int, parent_y: int):
        super().compute_position(parent_x, parent_y)
        y = parent_y
        for child in self.contents:
            child.compute_position(parent_x, y)
            y += child.height

    # overrides method from parent
    def traverse(self):
        for child in self.contents:
            yield from child.traverse()

    # overrides method from parent
    def paint(self, buffer):
        for item in self.contents:
            item.paint(buffer)
