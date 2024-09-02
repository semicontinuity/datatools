from typing import List

from datatools.misc.expenses.app import ExpensesNode
from datatools.misc.expenses.viewer.model.JFolder import JFolder
from datatools.misc.expenses.viewer.model.JLeaf import JLeaf
from datatools.misc.expenses.viewer.model.JValueElement import JValueElement
from datatools.tui.treeview.treenode_context import TreeNodeContext

INDENT = 2


class ViewModel(TreeNodeContext):
    key_field_length: int
    total: float

    def __init__(self, root: ExpensesNode) -> None:
        self.expenses = root
        self.key_field_length = root.max_indent_and_key_length()
        self.width = 120
        self.total = root.value

    def build_root_model(self):
        return self.build_model_raw(self.expenses)

    def build_model(self, node: ExpensesNode, parent: JValueElement = None, last_in_parent=True) -> JValueElement:
        model = self.build_model_raw(node, last_in_parent)
        model.parent = parent
        return model

    def build_model_raw(self, node: ExpensesNode, last_in_parent=True) -> JValueElement:
        text = node.key + ' ' * (self.key_field_length - len(node.key) - node.indent)
        if len(node.items) == 0:
            n = JLeaf(node.value, text, node.indent, last_in_parent)
            n.context = self
            return n
        else:
            folder = JFolder(node.value, text, node.indent, last_in_parent)
            folder.set_elements(self.build_array_items_models(node.items, folder))
            folder.context = self
            folder.start.context = self
            return folder

    def build_array_items_models(self, v: List, parent: JValueElement) -> List[JValueElement]:
        items = []
        size = len(v)
        for i, item in enumerate(v):
            items.append(self.build_model(item, parent, i >= size - 1))
            i += 1
        return items
