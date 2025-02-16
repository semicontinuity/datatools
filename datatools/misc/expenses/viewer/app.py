#!/usr/bin/env python3

import sys

from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.misc.expenses.app import ExpensesTreeReader
from datatools.misc.expenses.viewer.expenses_document import ExpensesDocument
from datatools.misc.expenses.viewer.expenses_grid import ExpensesGrid
from datatools.misc.expenses.viewer.highlighting.highlighting import Highlighting, ConsoleHighlighting
from datatools.misc.expenses.viewer.model import ViewModel
from datatools.tui.exit_codes_v2 import EXIT_CODE_ESCAPE
from datatools.tui.grid_base import WGridBase
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview.tree_grid_context import TreeGridContext
from datatools.tui.treeview.tree_grid_factory import tree_grid
from datatools.tui.treeview.tree_document import TreeDocument
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
        'jv',
        tree_grid(document, grid_context, grid_class=ExpensesGrid),
        DataBundle(None, None, None, None, None),
        popup
    )


def make_document(j):
    model = ViewModel(j).build_root_model()
    model.set_collapsed_recursive(True)
    model.collapsed = False
    return ExpensesDocument(model)


def loop(document: ExpensesDocument):
    g: WGridBase = make_json_tree_applet(document).g
    g.loop()
    return EXIT_CODE_ESCAPE, None


def main():
    global doc
    init_object_exporter()
    Highlighting.CURRENT = ConsoleHighlighting()
    expenses = ExpensesTreeReader(sys.argv[1]).read()
    expenses.calculate_value()
    doc = make_document(expenses)  # must consume stdin first
    exit_code, output = with_alternate_screen(lambda: loop(doc))


if __name__ == "__main__":
    main()
