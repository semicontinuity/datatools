from typing import AnyStr, Tuple, List

from datatools.tui.treeview.rich_text import Style


class TreeNode:

    last_in_parent: bool

    parent: 'TreeNode'
    line: int
    size: int
    collapsed: bool

    def __init__(self, last_in_parent=True) -> None:
        self.last_in_parent = last_in_parent
        self.collapsed = False

    def __iter__(self):
        """ Iterates over visible child nodes, if any (or self, if node is a leaf) """
        yield self

    def layout(self, line: int) -> int:
        self.line = line
        self.size = 1
        return line + 1

    def text_length(self) -> int:
        return sum((len(span[0]) for span in self.spans()))

    def rich_text(self) -> Tuple[AnyStr, Style]: pass

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        pass

    def optimize_layout(self, height): pass

    def set_collapsed_recursive(self, collapsed: bool):
        self.collapsed = collapsed
