#!/usr/bin/env python3

import json
import sys
from dataclasses import dataclass

from datatools.json.json2ansi_toolkit import Style, AnsiToolkit
from datatools.json.structure_discovery import Discovery
from datatools.json2ansi.default_style import default_style
from datatools.json2ansi.grid import WGrid
from datatools.jt.app.app_kit import Applet
from datatools.jt.model.data_bundle import DataBundle
from datatools.jt.model.metadata import Metadata
from datatools.jt.model.presentation import Presentation
from datatools.tui.json2ansi_buffer import Buffer
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


def grid(screen_buffer: Buffer, grid_context: GridContext) -> WGrid:

    def cell_value(line, column):
        return "-"

    g = WGrid(grid_context.x, grid_context.y, grid_context.width, grid_context.height, screen_buffer, cell_value, grid_context.interactive)
    g.total_lines = screen_buffer.height
    return g


def make_json2ansi_applet(j, style: Style = default_style(), state=None, popup: bool = False):
    state = {} if state is None else state
    screen_buffer = paint_screen_buffer(j, style)
    grid_context = auto_position(screen_buffer, state)
    return do_make_json2ansi_applet(grid_context, j, popup, screen_buffer, state)


def do_make_json2ansi_applet(grid_context, j, popup, screen_buffer, state):
    return Applet(
        'json2ansi',
        grid(screen_buffer, grid_context),
        DataBundle(j, Metadata(), Presentation(), state),
        popup
    )


def paint_screen_buffer(j, style) -> Buffer:
    return AnsiToolkit(Discovery(), style, primitive_max_width=None).page_node(j).paint()


def main():
    fd_tui = infer_fd_tui()
    patch_picotui(fd_tui, fd_tui)

    if len(sys.argv) > 1 and sys.argv[1] == '-q':
        j = data()
        screen_buffer = paint_screen_buffer(j, default_style())
        screen_size = screen_size_or_default()
        screen_buffer.flush(*screen_size)
        return

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
    main()
