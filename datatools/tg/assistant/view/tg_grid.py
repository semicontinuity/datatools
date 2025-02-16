from picotui.defs import KEY_RIGHT

from datatools.tui.treeview.tree_grid import TreeGrid
from datatools.tui.treeview.tree_document import TreeDocument


class TgGrid(TreeGrid):

    def __init__(self, x: int, y: int, width, height, document: TreeDocument, interactive=True):
        super().__init__(x, y, width, height, document, interactive)

    def handle_cursor_keys(self, key):
        if key == KEY_RIGHT:
            self.document.visit(self.cur_line)
        return super().handle_cursor_keys(key)
