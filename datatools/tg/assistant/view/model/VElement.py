from typing import AnyStr, Tuple, List

from datatools.tui.treeview.rich_text import Style
from datatools.tui.treeview.treenode import TreeNode


class VElement(TreeNode):

    indent: int

    def __init__(self) -> None:
        super().__init__(True)
        self.indent = 0

    # @override
    def spans(self, render_state=None) -> List[Tuple[AnyStr, Style]]:
        return [(' ' * self.indent, Style())] + [self.rich_text()]

    def rich_text(self) -> Tuple[AnyStr, Style]: pass
