from typing import List

from datatools.misc.expenses.app import ExpensesNode
from datatools.misc.expenses.viewer.model.JFolder import JFolder
from datatools.misc.expenses.viewer.model.JLeaf import JLeaf
from datatools.misc.expenses.viewer.model.JValueElement import JValueElement
from datatools.tui.treeview.tree_node_context import TreeNodeContext

INDENT = 2


class ViewModel(TreeNodeContext):
    key_field_length: int
    ref_amount: float

    def __init__(self, root: ExpensesNode, indent_offset: int = 0) -> None:
        self.expenses = root
        self.indent_offset = indent_offset
        self.key_field_length = self._max_width(root)
        self.width = 120
        self.ref_amount = max((item.value for item in root.items)) if root.items else root.value

    def _max_width(self, node: ExpensesNode) -> int:
        own = node.indent - self.indent_offset + len(node.key)
        children = max((self._max_width(item) for item in node.items), default=0)
        return max(own, children)

    def build_root_model(self):
        return self.build_model_raw(self.expenses)

    def build_model(self, node: ExpensesNode, parent: JValueElement = None, last_in_parent=True) -> JValueElement:
        model = self.build_model_raw(node, last_in_parent)
        model.parent = parent
        return model

    def build_model_raw(self, node: ExpensesNode, last_in_parent=True) -> JValueElement:
        effective_indent = node.indent - self.indent_offset
        text = node.key + ' ' * (self.key_field_length - len(node.key) - effective_indent)
        if len(node.items) == 0:
            n = JLeaf(node.value, text, effective_indent, last_in_parent)
            n.context = self
            n.expenses_node = node
            return n
        else:
            folder = JFolder(node.value, text, effective_indent, last_in_parent)
            folder.set_elements(self.build_array_items_models(node.items, folder))
            folder.context = self
            folder.start.context = self
            folder.expenses_node = node
            return folder

    def build_array_items_models(self, v: List, parent: JValueElement) -> List[JValueElement]:
        items = []
        size = len(v)
        for i, item in enumerate(v):
            items.append(self.build_model(item, parent, i >= size - 1))
            i += 1
        return items
