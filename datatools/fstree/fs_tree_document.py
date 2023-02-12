from pathlib import Path
from typing import List

from datatools.fstree.fs_tree_model import FsInvisibleRoot, populate_children
from datatools.tui.treeview.grid import WGrid
from datatools.tui.treeview.treedocument import TreeDocument


class FsTreeDocument(TreeDocument):

    listener: WGrid

    def __init__(self, root_folder: str) -> None:
        root_path = Path(root_folder)
        root_node = FsInvisibleRoot(root_path.name)
        populate_children(root_node, root_path)
        super().__init__(root_node)
        self.root_folder = root_folder
        self.root_path = root_path
        self.listener = None

    # should return True if it was actually refreshed
    def refresh(self):
        populate_children(self.root, self.root_path)
        self.layout()
        if self.listener is not None:
            self.listener.request_redraw()

    def get_selected_path(self, line) -> str:
        return self.root_folder + '/' + '/'.join(self.selected_path(line))

    # does not work for empty dirs, fix
    def selected_path(self, line) -> List[str]:
        path: List[str] = []
        node = self.rows[line]
        while True:
            path.append(node.name)
            node = node.parent
            if node is self.root:
                return list(reversed(path))

    def collapse(self, line) -> int:
        element = self.rows[line]
        if element.collapsed:
            element = element.parent
        if element is not None:
            element.collapsed = True
            return element.line
        else:
            return line
