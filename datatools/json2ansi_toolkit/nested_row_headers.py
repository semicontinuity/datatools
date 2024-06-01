from typing import List

from datatools.json2ansi_toolkit.header_node import HeaderNode
from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.blocks.hbox import HBox
from datatools.tui.buffer.blocks.vbox import VBox


class NestedRowHeaders(VBox):
    leaves: List[Block]

    def __init__(self, contents, leaves: List[Block]):
        super().__init__(contents)
        self.leaves = leaves

    def compute_height(self) -> List[int]:
        super(NestedRowHeaders, self).compute_height()
        return [leaf.width for leaf in self.leaves]

    def compute_widths(self) -> List[int]:
        super(NestedRowHeaders, self).compute_widths()
        return [leaf.width for leaf in self.leaves]

    def set_min_heights(self, sizes: List[int]):
        for i in range(len(sizes)):
            self.leaves[i].set_min_height(sizes[i])

    def max_level_widths(self) -> List[int]:
        result = []
        self.max_level_widths0(result, 0, self.contents)
        return result

    def max_level_widths0(self, widths: List[int], index: int, contents: List[HBox]):
        if index >= len(widths):
            widths.append(0)
        for block in contents:
            if type(block) is HeaderNode:
                widths[index] = max(widths[index], block.width)
            else:
                widths[index] = max(widths[index], block.contents[0].width)
                self.max_level_widths0(widths, index + 1, block.contents[1].contents)

    def set_level_widths(self, sizes: List[int]):
        self.set_level_widths0(sizes, 0, self.contents)

    def set_level_widths0(self, sizes: List[int], index: int, contents: List[HBox]):
        for block in contents:
            if type(block) is HeaderNode:
                block.set_min_width(sizes[index])
            else:
                block.contents[0].set_min_width(sizes[index])
                self.set_level_widths0(sizes, index + 1, block.contents[1].contents)
