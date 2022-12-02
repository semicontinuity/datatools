#!/usr/bin/env python3

import json
import sys
from dataclasses import dataclass

from datatools.json.json2ansi_toolkit import Style
from datatools.json2ansi.default_style import default_style
from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.jt.model.metadata import Metadata
from datatools.jt.model.presentation import Presentation
from datatools.jv.drawable import Drawable
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


def auto_position(screen_buffer, state):
    screen_width, screen_height = screen_size_or_default()
    if "anchor" in state:
        anchor_y = state["anchor"]["y"]
        if anchor_y > screen_height / 2:
            y = anchor_y - screen_buffer.height
        else:
            y = anchor_y + 1
        x = max(0, (screen_width - screen_buffer.width) // 2)
    else:
        y = 0
        x = 0
    grid_context = GridContext(x, y, screen_width, screen_height)
    return grid_context


def grid(drawable: Drawable, grid_context: GridContext) -> WGrid:
    g = WGrid(grid_context.x, grid_context.y, grid_context.width, grid_context.height, drawable, grid_context.interactive)
    g.layout()
    return g


def make_json2ansi_applet(j, style: Style = default_style(), state=None, popup: bool = False):
    state = {} if state is None else state
    drawable = paint_data(j, style)
    grid_context = auto_position(drawable, state)
    return do_make_json2ansi_applet(grid_context, j, popup, drawable, state)


def do_make_json2ansi_applet(grid_context, j, popup, drawable: Drawable, state):
    return Applet(
        'json2ansi',
        grid(drawable, grid_context),
        DataBundle(j, Metadata(), Presentation(), state),
        popup
    )


def paint_data(j, style) -> Drawable:
    return Drawable(build_model(None, j))


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
    return run(lambda: make_json2ansi_applet(data()).run())


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    return json.loads(s)


if __name__ == "__main__":
    Highlighting.CURRENT = ConsoleHighlighting()
    main()
