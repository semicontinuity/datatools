from typing import List

from datatools.misc.expenses import ExpensesNode
from datatools.misc.tree_table.jv.model.JElement import JElement
from datatools.misc.tree_table.jv.model.JFolder import JFolder
from datatools.misc.tree_table.jv.model.JString import JString
from datatools.misc.tree_table.jv.model.JValueElement import JValueElement

INDENT = 2


def build_root_model(expenses: ExpensesNode):
    # array = JFolder(50, "text")
    # child1 = JString(10, "child 1", 2, False)
    # child2 = JString(20, "child 2", 2, True)
    # array.set_elements([child1, child2])
    #
    # return array
    return build_model_raw(expenses)


def build_model_raw(node: ExpensesNode, last_in_parent=True) -> JValueElement:
    if len(node.items) == 0:
        return JString(node.value, node.key, node.indent, last_in_parent)
    else:
        array = JFolder(node.value, node.key, node.indent, last_in_parent)
        array.set_elements(build_array_items_models(node.items))
        return array


def build_array_items_models(v: List) -> List[JValueElement]:
    items = []
    size = len(v)
    for i, v in enumerate(v):
        items.append(build_model_raw(v, i >= size - 1))
        i += 1
    return items
