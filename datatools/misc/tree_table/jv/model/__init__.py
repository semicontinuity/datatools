from typing import List

from datatools.misc.expenses import ExpensesNode
from datatools.misc.tree_table.jv.model.JElement import JElement
from datatools.misc.tree_table.jv.model.JFolder import JFolder
from datatools.misc.tree_table.jv.model.JString import JString
from datatools.misc.tree_table.jv.model.JValueElement import JValueElement

INDENT = 2


def build_root_model(expenses: ExpensesNode):
    key_field_length = expenses.max_indent_and_key_length()
    return build_model_raw(key_field_length, expenses)


def build_model(key_field_length: int, node: ExpensesNode, parent: JValueElement = None, last_in_parent=True) -> JValueElement:
    model = build_model_raw(key_field_length, node, last_in_parent)
    model.parent = parent
    return model


def build_model_raw(key_field_length: int, node: ExpensesNode, last_in_parent=True) -> JValueElement:
    text = node.key + ' ' * (key_field_length - len(node.key) - node.indent)
    if len(node.items) == 0:
        return JString(node.value, text, node.indent, last_in_parent)
    else:
        folder = JFolder(node.value, text, node.indent, last_in_parent)
        folder.set_elements(build_array_items_models(key_field_length, node.items, folder))
        return folder


def build_array_items_models(key_field_length: int, v: List, parent: JValueElement) -> List[JValueElement]:
    items = []
    size = len(v)
    for i, item in enumerate(v):
        items.append(build_model(key_field_length, item, parent, i >= size - 1))
        i += 1
    return items
