#!/usr/bin/env python3

import json
import sys

from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.jv.document import JDocument
from datatools.jv.highlighting.highlighting import Highlighting, ConsoleHighlighting
from datatools.jv.model import build_model
from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import *
from datatools.tui.picotui_util import with_prepared_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview.grid import GridContext, grid
from datatools.tui.treeview.treedocument import TreeDocument
from datatools.tui.tui_fd import infer_fd_tui


def make_json_tree_applet(document, popup: bool = False):
    screen_width, screen_height = screen_size_or_default()
    grid_context = GridContext(0, 0, screen_width, screen_height)
    document.layout()
    document.optimize_layout(screen_height)
    document.layout()
    return do_make_json_tree_applet(grid_context, popup, document)


def make_document(j):
    model = build_model(j)
    model.set_collapsed_recursive(True)
    model.collapsed = False
    return JDocument(model)


def do_make_json_tree_applet(grid_context, popup, document: TreeDocument):
    return Applet(
        'jv',
        grid(document, grid_context),
        DataBundle(None, None, None, None),
        popup
    )


def with_alternate_screen():
    fd_tui = infer_fd_tui()
    patch_picotui(fd_tui, fd_tui)

    try:
        cursor_position_save()
        Screen.init_tty()
        screen_alt()
        return with_prepared_screen(lambda: make_json_tree_applet(make_document(data())).run())
    finally:
        screen_regular()
        Screen.deinit_tty()
        cursor_position_restore()


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    return json.loads(s)


if __name__ == "__main__":
    Highlighting.CURRENT = ConsoleHighlighting()
    with_alternate_screen()
