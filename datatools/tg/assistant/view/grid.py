from datatools.tui.treeview.grid import WGrid
from datatools.tui.treeview.treedocument import TreeDocument


class TgGrid(WGrid):

    def __init__(self, x: int, y: int, width, height, document: TreeDocument, interactive=True):
        super().__init__(x, y, width, height, document, interactive)
