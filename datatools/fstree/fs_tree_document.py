from datatools.tui.treeview.treedocument import TreeDocument
from datatools.tui.treeview.treenode import TreeNode


class FsTreeDocument(TreeDocument):
    def __init__(self, root: TreeNode, root_folder: str) -> None:
        super().__init__(root)
        self.root_folder = root_folder

    def get_selected_path(self, line) -> str:
        path = []
        node = self.rows[line]
        while True:
            path.append(node.name)
            node = node.parent
            if node is None:
                return self.root_folder + '/' + '/'.join(reversed(path))
