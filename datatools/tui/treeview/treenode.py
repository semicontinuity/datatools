from typing import AnyStr, Tuple, List, Optional

from datatools.tui.treeview.render_state import RenderState
from datatools.tui.treeview.rich_text import Style


class TreeNode:

    last_in_parent: bool

    parent: Optional['TreeNode']
    line: int  # y position (in lines)
    size: int  # size (in lines)
    collapsed: bool

    def __init__(self, last_in_parent=True) -> None:
        self.last_in_parent = last_in_parent
        self.collapsed = False
        self.parent = None

    def __iter__(self):
        """ Iterates over visible child nodes, if any (or self, if node is a leaf) """
        yield self

    def layout(self, line: int) -> int:
        self.line = line
        self.size = 1
        return line + 1

    def text_length(self) -> int:
        return sum((len(span[0]) for span in self.spans()))

    def spans(self, render_state: RenderState = None) -> List[Tuple[AnyStr, Style]]:
        pass

    def optimize_layout(self, height): pass

    def set_collapsed_recursive(self, collapsed: bool):
        self.collapsed = collapsed

    def custom_action(self, action: str, line: int):
        pass
