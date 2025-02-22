from datatools.tui.treeview.tree_node import TreeNode


def compact(node: TreeNode) -> TreeNode:
    node.set_collapsed_recursive(True)
    node.collapsed = False
    return node
