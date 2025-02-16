from datatools.tui.treeview.tree_grid_context import TreeGridContext
from datatools.tui.treeview.dynamic_editor_support import DynamicEditorSupport
from datatools.tui.treeview.tree_grid import TreeGrid
from datatools.tui.treeview.tree_document import TreeDocument


def tree_grid(document: TreeDocument, grid_context: TreeGridContext, grid_class=TreeGrid) -> TreeGrid:
    height = grid_context.height if grid_context.interactive else min(grid_context.height, document.height)
    g = grid_class(
        grid_context.x,
        grid_context.y,
        grid_context.width,
        height,
        document,
        grid_context.interactive
    )
    g.dynamic_helper = DynamicEditorSupport(grid_context.height, g)
    g.layout()
    return g
