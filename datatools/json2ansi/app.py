#!/usr/bin/env python3
import json
import sys

from datatools.json.json2ansi_toolkit import AnsiToolkit
from datatools.json.structure_discovery import Discovery
from datatools.json2ansi.grid import WGrid
from datatools.json2ansi.style import style
from datatools.jt.app import App
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import run
from datatools.tui.terminal import read_screen_size, with_raw_terminal


def grid(state, presentation, screen_size, j, column_keys) -> WGrid:
    page_node = AnsiToolkit(Discovery(), style(), primitive_max_width=None).page_node(j)
    screen_buffer = page_node.paint()

    def cell_value(line, column):
        return "-"

    g = WGrid(screen_size[0], screen_size[1], screen_buffer, cell_value)
    g.total_lines = screen_buffer.height
    return g


def main(g, app):
    fd_tui = 2
    patch_picotui(fd_tui, fd_tui)

    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)

    screen_size = (1000, 10000)
    if sys.stdout.isatty():
        screen_size = with_raw_terminal(read_screen_size)
        screen_size = screen_size[0], screen_size[1] - 1    # something strange with the last line (autoscroll?)
    exit_code, state = run(lambda: app(g(None, None, screen_size, j, None)).run())
    sys.exit(exit_code)


if __name__ == "__main__":
    main(grid, App)
