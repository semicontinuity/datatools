from typing import List

from datatools.tui.treeview.treenode import TreeNode
from datatools.tui.treeview.rich_text import render_substr


class TreeDocument:
    root: TreeNode

    width: int
    height: int
    rows: List[TreeNode]

    def __init__(self, root: TreeNode) -> None:
        self.root = root

    def layout(self):
        width = 0
        height = 0
        rows = []

        for row in self.root:
            width = max(width, row.text_length())
            rows.append(row)
            height += 1

        self.root.layout(0)
        self.width = width
        self.height = height
        self.rows = rows

    def optimize_layout(self, height):
        self.root.optimize_layout(height)

    def row_to_string(self, y, x_from, x_to):
        if y < len(self.rows):
            return render_substr(self.rows[y].spans(), x_from, x_to)
        else:
            return ' ' * (x_to - x_from)

    def collapse(self, line) -> int:
        parent = self.rows[line].parent
        if parent is not None:
            parent.collapsed = True
            return parent.line
        else:
            return line

    def expand(self, line):
        self.rows[line].collapsed = False

    def expand_recursive(self, line) -> int:
        element = self.rows[line]
        element.set_collapsed_recursive(False)
        self.layout()
        return element.line
