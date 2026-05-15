#!/usr/bin/env python3

import os
import sys

from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.misc.expenses.app import ExpensesTreeReader, ExpensesNode
from datatools.misc.expenses.viewer.expenses_document import ExpensesDocument
from datatools.misc.expenses.viewer.expenses_grid import ExpensesGrid
from datatools.misc.expenses.viewer.highlighting.highlighting import Highlighting, ConsoleHighlighting
from datatools.misc.expenses.viewer.model import ViewModel
from datatools.tui.exit_codes_v2 import EXIT_CODE_ESCAPE
from datatools.tui.grid_base import WGridBase
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview.tree_document import TreeDocument
from datatools.tui.treeview.tree_grid_context import TreeGridContext
from datatools.tui.treeview.tree_grid_factory import tree_grid
from datatools.util.object_exporter import init_object_exporter


def make_json_tree_applet(document: ExpensesDocument, popup: bool = False) -> Applet:
    screen_width, screen_height = screen_size_or_default()
    grid_context = TreeGridContext(0, 0, screen_width, screen_height)
    document.layout()
    document.optimize_layout(screen_height)
    document.layout()
    return do_make_json_tree_applet(grid_context, popup, document)


def do_make_json_tree_applet(grid_context, popup, document: TreeDocument) -> Applet:
    return Applet(
        'expenses',
        tree_grid(document, grid_context, grid_class=ExpensesGrid),
        DataBundle(None, None, None, None, None),
        popup
    )


def make_document(expenses: ExpensesNode):
    model = ViewModel(expenses).build_root_model()
    model.set_collapsed_recursive(True)
    model.collapsed = False
    return ExpensesDocument(model)


def loop(document: ExpensesDocument):
    g: WGridBase = make_json_tree_applet(document).g
    g.loop()
    return EXIT_CODE_ESCAPE, None


def shift_indent(node: ExpensesNode, delta: int) -> ExpensesNode:
    node.indent += delta
    for child in node.items:
        shift_indent(child, delta)
    return node


def read_folder(folder: str) -> ExpensesNode:
    import glob
    files = sorted(glob.glob(os.path.join(folder, '*.txt')))
    sub_roots = [ExpensesTreeReader(f).read() for f in files]
    for sr in sub_roots:
        sr.calculate_value()
        shift_indent(sr, 2)
    total = sum(sr.value for sr in sub_roots)
    return ExpensesNode(0, os.path.basename(folder), total, sub_roots)


def main():
    global doc
    init_object_exporter()
    Highlighting.CURRENT = ConsoleHighlighting()
    path = sys.argv[1]
    if os.path.isdir(path):
        expenses = read_folder(path)
    else:
        expenses = ExpensesTreeReader(path).read()
        expenses.calculate_value()
    doc = make_document(expenses)  # must consume stdin first
    exit_code, output = with_alternate_screen(lambda: loop(doc))


if __name__ == "__main__":
    main()
