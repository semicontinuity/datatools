from typing import List, Optional

from datatools.tui.ansi_str import ANSI_CMD_DEFAULT_BG
from datatools.tui.terminal import ansi_background_escape_code
from datatools.tui.treeview.render_state import RenderState
from datatools.tui.treeview.rich_text import render_spans_substr
from datatools.tui.treeview.tree_node import TreeNode


class TreeDocument:
    footer: Optional[str] = None

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
            s = render_spans_substr(self.rows[y].spans(render_state), x_from, x_to)
            return ansi_background_escape_code(48, 48, 48) + s + ANSI_CMD_DEFAULT_BG if render_state.is_under_cursor else s
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

    def collapse_recursive(self, line: int, collapsed: bool = True) -> int:
        element = self.rows[line]
        element.set_collapsed_recursive(collapsed)
        self.layout()
        return element.line

    def collapse_children(self, line: int, collapsed: bool = True) -> int:
        element = self.rows[line]
        element.set_collapsed_children(collapsed)
        self.layout()
        return element.line
