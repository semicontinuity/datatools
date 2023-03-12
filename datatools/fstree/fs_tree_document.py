from pathlib import Path
from typing import List, Optional

from datatools.fstree.fs_tree_model import FsInvisibleRoot, FsFolder
from datatools.tui.treeview.grid import WGrid
from datatools.tui.treeview.treedocument import TreeDocument


class FsTreeDocument(TreeDocument):

    listener: WGrid

    def __init__(self, root_folder: str) -> None:
        root_path = Path(root_folder)
        root_node = FsInvisibleRoot(root_path, root_path.name)
        root_node.refresh()
        super().__init__(root_node)
        self.root_folder = root_folder
        self.root_path = root_path
        self.listener = None

    # should return True if it was actually refreshed
    def refresh(self):
        self.root.refresh()
        if self.listener is not None and not self.root.is_empty():
            self.layout_for_height(self.listener.dynamic_helper.screen_height)
            self.listener.layout()
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

    def get_node(self, line) -> Optional[FsFolder]:
        return None if line < 0 or line >= self.height else self.rows[line]
