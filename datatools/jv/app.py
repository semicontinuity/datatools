#!/usr/bin/env python3

import json
import sys
from dataclasses import dataclass

from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.jt.model.metadata import Metadata
from datatools.jt.model.presentation import Presentation
from datatools.jv.model.document import Document
from datatools.jv.grid import WGrid
from datatools.jv.highlighting.highlighting import Highlighting, ConsoleHighlighting
from datatools.jv.model import build_model
from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import *
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.tui_fd import infer_fd_tui


@dataclass
class GridContext:
    x: int
    y: int
    width: int
    height: int
    interactive: bool = True


def auto_position(drawable, state):
    screen_width, screen_height = screen_size_or_default()
    if "anchor" in state:
        anchor_y = state["anchor"]["y"]
        if anchor_y > screen_height / 2:
            y = anchor_y - drawable.height
        else:
            y = anchor_y + 1
        x = max(0, (screen_width - drawable.width) // 2)
    else:
        y = 0
        x = 0
    return GridContext(x, y, screen_width, screen_height)


def grid(drawable: Document, grid_context: GridContext) -> WGrid:
    g = WGrid(grid_context.x, grid_context.y, grid_context.width, grid_context.height, drawable, grid_context.interactive)
    g.layout()
    return g


def make_json_tree_applet(j, state=None, popup: bool = False):
    state = {} if state is None else state
    screen_width, screen_height = screen_size_or_default()
    grid_context = GridContext(0, 0, screen_width, screen_height)
    model = build_model(None, None, j)
    model.collapsed = False
    drawable = Document(model)
    drawable.layout()
    drawable.optimize_layout(screen_height)
    drawable.layout()
    return do_make_json_tree_applet(grid_context, j, popup, drawable, state)


def do_make_json_tree_applet(grid_context, j, popup, drawable: Document, state):
    return Applet(
        'json2ansi',
        grid(drawable, grid_context),
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
