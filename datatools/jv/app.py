#!/usr/bin/env python3

import json
import sys

from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.jt.model.metadata import Metadata
from datatools.jt.model.presentation import Presentation
from datatools.jv.document import JDocument
from datatools.jv.highlighting.highlighting import Highlighting, ConsoleHighlighting
from datatools.jv.model import build_model
from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import *
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview.grid import GridContext, grid
from datatools.tui.treeview.treedocument import TreeDocument
from datatools.tui.tui_fd import infer_fd_tui


def make_json_tree_applet(j, state=None, popup: bool = False):
    state = {} if state is None else state
    screen_width, screen_height = screen_size_or_default()
    grid_context = GridContext(0, 0, screen_width, screen_height)
    model = build_model(j)
    model.set_collapsed_recursive(True)
    model.collapsed = False
    document = JDocument(model)
    document.layout()
    document.optimize_layout(screen_height)
    document.layout()
    return do_make_json_tree_applet(grid_context, j, popup, document, state)


def do_make_json_tree_applet(grid_context, j, popup, document: TreeDocument, state):
    return Applet(
        'jv',
        grid(document, grid_context),
        DataBundle(j, Metadata(), Presentation(), state),
        popup
    )


def main():
    fd_tui = infer_fd_tui()
    patch_picotui(fd_tui, fd_tui)

    try:
        cursor_position_save()
        Screen.init_tty()
        screen_alt()
        sys.exit(do_main())
    finally:
        screen_regular()
        Screen.deinit_tty()
        cursor_position_restore()


def do_main():
    return run(lambda: make_json_tree_applet(data()).run())


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    return json.loads(s)


if __name__ == "__main__":
    Highlighting.CURRENT = ConsoleHighlighting()
    main()
