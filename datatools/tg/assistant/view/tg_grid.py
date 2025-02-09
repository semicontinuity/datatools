from picotui.defs import KEY_RIGHT

from datatools.tui.treeview.grid import WGrid
from datatools.tui.treeview.treedocument import TreeDocument


class TgGrid(WGrid):

    def __init__(self, x: int, y: int, width, height, document: TreeDocument, interactive=True):
        super().__init__(x, y, width, height, document, interactive)

    def handle_cursor_keys(self, key):
        if key == KEY_RIGHT:
            self.document.visit(self.cur_line)
        return super().handle_cursor_keys(key)
