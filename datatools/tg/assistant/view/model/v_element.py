from typing import AnyStr

from datatools.tui.rich_text import Style
from datatools.tui.treeview.tree_node import TreeNode


class VElement(TreeNode):
    text: str
    indent: int

    def __init__(self, text: str) -> None:
        super().__init__(True)
        self.indent = 0
        self.text = text

    # @override
    def spans(self, render_state=None) -> list[tuple[AnyStr, Style]]:
        return [(' ' * self.indent, Style())] + self.rich_text()

    def rich_text(self) -> list[tuple[AnyStr, Style]]:
        return [(self.text, self.text_style())]

    def text_style(self) -> Style: pass

    def indent_recursive(self, indent: int):
        self.indent = indent

    def count_unread_children(self):
        pass

    # abstract
    def visit(self):
        pass

    # abstract
    def visit_recursive(self):
        pass
