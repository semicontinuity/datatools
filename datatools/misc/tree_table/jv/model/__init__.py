from typing import List

from datatools.misc.expenses import ExpensesNode
from datatools.misc.tree_table.jv.model.JElement import JElement
from datatools.misc.tree_table.jv.model.JFolder import JFolder
from datatools.misc.tree_table.jv.model.JString import JString
from datatools.misc.tree_table.jv.model.JValueElement import JValueElement

INDENT = 2


def build_root_model(expenses: ExpensesNode):
    return build_model_raw(expenses)


def build_model(node: ExpensesNode, parent: JValueElement = None, last_in_parent=True) -> JValueElement:
    model = build_model_raw(node, last_in_parent)
    model.parent = parent
    return model


def build_model_raw(node: ExpensesNode, last_in_parent=True) -> JValueElement:
    if len(node.items) == 0:
        return JString(node.value, node.key, node.indent, last_in_parent)
    else:
        folder = JFolder(node.value, node.key, node.indent, last_in_parent)
        folder.set_elements(build_array_items_models(node.items, folder))
        return folder


def build_array_items_models(v: List, parent: JValueElement) -> List[JValueElement]:
    items = []
    size = len(v)
    for i, item in enumerate(v):
        items.append(build_model(item, parent, i >= size - 1))
        i += 1
    return items
