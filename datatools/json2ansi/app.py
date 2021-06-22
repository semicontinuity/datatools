#!/usr/bin/env python3
import json
import sys

from datatools.json.json2ansi_toolkit import AnsiToolkit
from datatools.json.structure_discovery import Discovery
from datatools.json2ansi.grid import WGrid
from datatools.json2ansi.style import style
from datatools.jt.app import App
from datatools.tui.picotui_patch import patch_picotui, isatty
from datatools.tui.picotui_util import run
from datatools.tui.terminal import read_screen_size, with_raw_terminal


def grid(screen_size, j) -> WGrid:
    page_node = AnsiToolkit(Discovery(), style(), primitive_max_width=None).page_node(j)
    screen_buffer = page_node.paint()

    def cell_value(line, column):
        return "-"

    g = WGrid(screen_size[0], screen_size[1], screen_buffer, cell_value)
    g.total_lines = screen_buffer.height
    return g


def make_json2ansi_app(j):
    screen_size = (1000, 10000)
    if isatty():
        screen_size = with_raw_terminal(read_screen_size)
    return App(grid(screen_size, j))


def main():
    patch_picotui()

    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)

    exit_code, state = run(lambda: make_json2ansi_app(j).run())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
