from picotui.defs import KEY_RIGHT, KEY_DELETE

from datatools.tui.treeview.tree_document import TreeDocument
from datatools.tui.treeview.tree_grid import TreeGrid


class TgGrid(TreeGrid):

    def __init__(self, x: int, y: int, width, height, document: TreeDocument, interactive=True):
        super().__init__(x, y, width, height, document, interactive)

    def handle_cursor_keys(self, key):
        if key == KEY_DELETE:
            self.document.visit_recursive(self.cur_line)
            self.redraw()
            return True
        elif key == KEY_RIGHT:
            self.document.visit(self.cur_line)

        return super().handle_cursor_keys(key)
