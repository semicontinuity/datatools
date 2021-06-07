#!/usr/bin/env python3
import json
import sys
from typing import List

from datatools.jt.app import load_data, parse_args, run, App
from datatools.jt.auto_coloring import max_column_widths, analyze_data, pick_displayed_columns
from datatools.jt.cell_renderer import column_renderers
from datatools.jtng.grid import WGrid
from datatools.tui.terminal import with_raw_terminal, read_screen_size
from datatools.util.conf import read_fd_or_default, write_fd_or_pass, fd_exists

FD_TUI = 103

FD_METADATA_IN = 104
FD_METADATA_OUT = 105

FD_PRESENTATION_IN = 106
FD_PRESENTATION_OUT = 107

FD_STATE_IN = 108
FD_STATE_OUT = 109

from datatools.tui.picotui_patch import patch_picotui
from datatools.jt.exit_codes_mapping import *


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def grid(state, presentation, screen_size, orig_data, column_keys) -> WGrid:
    column_titles: List[str] = [c for c in column_keys]
    column_widths: List[int] = [max_column_widths[c] for c in column_keys]

    g = WGrid(
        presentation.get("title"), screen_size[0], screen_size[1], column_titles, column_widths, column_keys,
        column_renderers(column_keys, presentation["columns"]).__getitem__,
        lambda line, column: orig_data[line].get(column_keys[column])
    )
    g.total_lines = len(orig_data)

    top_line = state["top_line"]
    if 0 <= top_line < g.total_lines:
        g.top_line = top_line

    cur_line = state["cur_line"]
    if top_line <= cur_line < g.total_lines:
        g.cur_line = cur_line

    return g


def main():
    presentation = read_fd_or_default(fd=FD_PRESENTATION_IN, default={})
    state = read_fd_or_default(fd=FD_STATE_IN, default={'top_line': 0, 'cur_line': 0})
    params = parse_args(sys.argv, presentation)
    fd_tui = FD_TUI if fd_exists(FD_TUI) else 2
    patch_picotui(fd_tui, fd_tui)

    orig_data = load_data(params)
    analyze_data(orig_data, params.columns.__contains__)

    screen_size = with_raw_terminal(read_screen_size)
    column_keys = pick_displayed_columns(screen_size[0])

    g = grid(state, presentation, screen_size, orig_data, column_keys)
    exit_code, state = run(lambda: App(g).run())

    write_fd_or_pass(FD_STATE_OUT, state)
    write_fd_or_pass(FD_PRESENTATION_OUT, presentation)
    if exit_code < 120:
        if (exit_code // EXIT_CODE_SHIFT) & 1 == 1:
            print(json.dumps(orig_data))
            sys.exit(exit_code)
    if exit_code != EXIT_CODE_ESCAPE:
        print(json.dumps(orig_data[state["cur_line"]]))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
