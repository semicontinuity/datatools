from typing import List

from datatools.tui.buffer.blocks.block import Block


class Container(Block):
    """
    Strange container of blocks, with functions, specific to HBox and VBox
    """
    contents: List[Block] = []

    def __init__(self, contents=None):
        self.contents = [] if contents is None else contents
        self.width = 0
        self.height = 0

    def compute_widths(self) -> List[int]:
        for child in self.contents:
            child.compute_width()
        return [child.width for child in self.contents]

    def compute_heights(self):
        for child in self.contents:
            child.compute_height()
        return [child.height for child in self.contents]

    def compute_width_as_max(self):
        """
        Sets the width of this container and all children to the width of the widest child.
        (VBox only?)
        """
        for child in self.contents:
            child.compute_width()
        self.width = max(child.width for child in self.contents)
        for child in self.contents:
            child.width = self.width

    def compute_height_as_max(self):
        """
        Sets the height of this container and all children to the height of the tallest child.
        (HBox only?)
        """
        for child in self.contents:
            child.compute_height()
        self.height = max((child.height for child in self.contents), default=0)
        for child in self.contents:
            child.height = self.height

    def compute_width_as_sum(self):
        """
        First step in laying out: compute width from widths of children.
        (HBox only?)
        """
        for child in self.contents:
            child.compute_width()
        self.width = sum(child.width for child in self.contents)

    def compute_height_as_sum(self):
        """
        First step in laying out: compute height from heights of children.
        (VBox only?)
        """
        for child in self.contents:
            child.compute_height()
        self.height = sum(child.height for child in self.contents)

    def set_min_widths(self, sizes: List[int]):
        for i in range(len(sizes)):
            self.contents[i].width = max(self.contents[i].width, sizes[i])

    def set_min_heights(self, heights: List[int]):
        for i in range(len(heights)):
            self.contents[i].height = max(self.contents[i].height, heights[i])

    def traverse(self):
        for child in self.contents:
            yield from child.traverse()

    def paint(self, buffer):
        for item in self.contents:
            item.paint(buffer)
