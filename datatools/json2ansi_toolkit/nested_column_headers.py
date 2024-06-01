from typing import List

from datatools.json2ansi_toolkit.header_node import HeaderNode
from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.blocks.hbox import HBox


class NestedColumnHeaders(HBox):
    leaves: List[Block]

    def __init__(self, contents, leaves: List[Block]):
        super().__init__(contents)
        self.leaves = leaves

    def compute_width(self):
        super(NestedColumnHeaders, self).compute_width()
        self.set_min_width(self.width)

    def compute_height(self):
        super(NestedColumnHeaders, self).compute_height()
        self.set_min_height(self.height)

    def compute_widths(self) -> List[int]:
        super(NestedColumnHeaders, self).compute_widths()
        return [leaf.width for leaf in self.leaves]

    def set_min_widths(self, sizes: List[int]):
        for i in range(len(sizes)):
            self.leaves[i].set_min_width(sizes[i])

    def max_level_heights(self) -> List[int]:
        result = []
        self.max_level_heights0(result, 0, self.contents)
        return result

    def max_level_heights0(self, sizes: List[int], index: int, contents: List[HBox]):
        if index >= len(sizes):
            sizes.append(0)
        for block in contents:
            if type(block) is HeaderNode:
                sizes[index] = max(sizes[index], block.height)
            else:
                sizes[index] = max(sizes[index], block.contents[0].height)
                self.max_level_heights0(sizes, index + 1, block.contents[1].contents)

    def set_level_heights(self, sizes: List[int]):
        self.set_level_heights0(sizes, 0, self.contents)

    def set_level_heights0(self, sizes: List[int], index: int, contents: List[HBox]):
        for block in contents:
            if type(block) is HeaderNode:
                block.set_min_height(sizes[index])
            else:
                block.contents[0].set_min_height(sizes[index])
                self.set_level_heights0(sizes, index + 1, block.contents[1].contents)
