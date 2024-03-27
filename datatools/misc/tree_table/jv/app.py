#!/usr/bin/env python3

import json
import sys

from picotui.defs import KEY_ENTER, KEY_F3, KEY_F4

from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.misc.expenses import ExpensesTreeReader
from datatools.misc.tree_table.jv.document import JDocument
from datatools.misc.tree_table.jv.grid import JGrid
from datatools.misc.tree_table.jv.highlighting.highlighting import Highlighting, ConsoleHighlighting
from datatools.misc.tree_table.jv.model import build_root_model
from datatools.tui.exit_codes_v2 import EXIT_CODE_ENTER, MODIFIER_ALT, EXIT_CODE_ESCAPE, EXIT_CODE_F3, EXIT_CODE_F4
from datatools.tui.picotui_keys import KEY_ALT_ENTER
from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import *
from datatools.tui.picotui_util import with_prepared_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview.grid import GridContext, grid
from datatools.tui.treeview.treedocument import TreeDocument
from datatools.tui.tui_fd import infer_fd_tui
from datatools.util.object_exporter import init_object_exporter


def make_json_tree_applet(document, popup: bool = False):
    screen_width, screen_height = screen_size_or_default()
    grid_context = GridContext(0, 0, screen_width, screen_height)
    document.layout()
    document.optimize_layout(screen_height)
    document.layout()
    return do_make_json_tree_applet(grid_context, popup, document)


def do_make_json_tree_applet(grid_context, popup, document: TreeDocument):
    return Applet(
        'jv',
        grid(document, grid_context, grid_class=JGrid),
        DataBundle(None, None, None, None, None),
        popup
    )


def with_alternate_screen(delegate):
    fd_tui = infer_fd_tui()
    patch_picotui(fd_tui, fd_tui)

    try:
        cursor_position_save()
        Screen.init_tty()
        screen_alt()
        return with_prepared_screen(delegate)
    finally:
        screen_regular()
        Screen.deinit_tty()
        cursor_position_restore()


def make_document(j):
    model = build_root_model(j)
    model.set_collapsed_recursive(True)
    model.collapsed = False
    return JDocument(model)


def loop(document: JDocument):
    g = make_json_tree_applet(document).g
    key_code = g.loop()
    if key_code == KEY_ENTER:
        return EXIT_CODE_ENTER, json.dumps(document.selected_value(g.cur_line))
    elif key_code == KEY_ALT_ENTER:
        return MODIFIER_ALT + EXIT_CODE_ENTER, document.selected_path(g.cur_line)
    elif key_code == KEY_F3:
        return EXIT_CODE_F3, json.dumps(document.selected_value(g.cur_line))
    elif key_code == KEY_F4:
        return EXIT_CODE_F4, json.dumps(document.selected_value(g.cur_line))
    else:
        return EXIT_CODE_ESCAPE, None


if __name__ == "__main__":
    init_object_exporter()
    Highlighting.CURRENT = ConsoleHighlighting()

    expenses = ExpensesTreeReader(sys.argv[1]).read()
    expenses.calculate_value()

    doc = make_document(expenses)    # must consume stdin first

    exit_code, output = with_alternate_screen(lambda: loop(doc))
