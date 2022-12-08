from typing import AnyStr, Tuple, List

from datatools.tui.treeview.treenode import TreeNode
from datatools.tui.treeview.rich_text import Style


class FsTreeNode(TreeNode):

    indent: int
    name: str
    padding: int

    def __init__(self, name: str, indent=0, last_in_parent=True) -> None:
        super().__init__(last_in_parent)
        self.name = name
        self.indent = indent
        self.padding = 0

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        return self.spans_for_indent() + [(self.name, Style())]

    def spans_for_indent(self) -> List[Tuple[AnyStr, Style]]:
        if self.indent == 0:
            return []
        else:
            return [(' ' * (self.indent - 2) + ('`-' if self.last_in_parent else '|-'), Style())]