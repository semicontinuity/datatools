from typing import List

from datatools.tui.treeview.render_state import RenderState
from datatools.tui.treeview.rich_text import render_spans_substr
from datatools.tui.treeview.treenode import TreeNode


class TreeDocument:
    root: TreeNode

    width: int
    height: int
    rows: List[TreeNode]

    def __init__(self, root: TreeNode) -> None:
        self.root = root

    def layout_for_height(self, height: int):
        self.layout()
        self.optimize_layout(height)
        self.layout()

    def layout(self):
        # Iterate over visible child nodes (recursively) to compute geometry
        width = 0
        height = 0
        rows = []

        for row in self.root:
            width = max(width, row.text_length())
            rows.append(row)
            height += 1

        self.rows = rows
        self.width = width
        self.height = height

        # Assign positions to each visible line (recursively)
        self.root.layout(0)

    def optimize_layout(self, height):
        self.root.optimize_layout(height)

    def row_to_string(self, y, x_from: int, x_to: int, render_state: RenderState):
        if y < len(self.rows):
            return render_spans_substr(self.rows[y].spans(render_state), x_from, x_to)
        else:
            return ' ' * (x_to - x_from)

    def collapse(self, line: int):
        pass

    def expand(self, line):
        self.rows[line].collapsed = False

    def expand_recursive(self, line) -> int:
        element = self.rows[line]
        element.set_collapsed_recursive(False)
        self.layout()
        return element.line
