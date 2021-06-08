#!/usr/bin/env python3
# ──────────────────────────────────────────────────────────────────────────────
# A tool for interactive selection of a row from TextUI-style table.
#
# arguments:
# [-s]: streaming mode
# [-t title]: title
# [json]: json with stripe colors specification
# like '{"column name":{"0":"ff0000", "1":"00ff00", "2":"8080ff"}}'
# corresponding data must look like "stripes": ["2","1","0","2"]
#
#
# STDIN: data as sequence of one-line jsons like {"field1":"value1", ... }
# result (json, corresponding to selected line) is printed to to STDOUT,
# if user has selected a row, or nothing, if user has cancelled selection.
#
# To paint UI and read keyboard, uses STDERR.
#
# Exit code corresponds to key code + sum of modifiers codes.
# ──────────────────────────────────────────────────────────────────────────────
import json
import signal
import sys
from json import JSONDecodeError
from typing import List

from datatools.jt.auto_coloring import max_column_widths, infer_presentation, pick_displayed_columns
from datatools.jt.auto_metadata import infer_metadata, compute_stats
from datatools.jt.cell_renderer import column_renderers
from datatools.jt.grid import WGrid
from datatools.tui.terminal import with_raw_terminal, read_screen_size, FD_TUI
from datatools.util.conf import read_fd_or_default, write_fd_or_pass, fd_exists, FD_PRESENTATION_IN, FD_STATE_IN, \
    FD_STATE_OUT, FD_PRESENTATION_OUT, FD_METADATA_IN

from dataclasses import dataclass

from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import *
from datatools.jt.exit_codes_mapping import *


@dataclass
class Params:
    title: str = None
    stream_mode: bool = None
    columns = {}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class App:
    g: WGrid

    def __init__(self, g):
        self.g = g
        signal.signal(signal.SIGWINCH, self.handle_sigwinch)

    def handle_sigwinch(self, signalNumber, frame):
        screen_size = Screen.screen_size()  # not very stable, sometimes duplicate 'x1b[8' is read
        self.g.width = screen_size[0]
        self.g.height = screen_size[1]
        self.g.redraw()

    def run(self):
        res = self.g.loop()
        exit_code = KEYS_TO_EXIT_CODES.get(res)
        state = {'top_line': self.g.top_line, 'cur_line': self.g.cur_line}
        return exit_code if exit_code is not None else EXIT_CODE_ESCAPE, state


def run(delegate):
    s = Screen()
    try:
        cursor_position_save()
        s.init_tty()
        s.cursor(False)
        screen_alt()
        s.cls()
        s.attr_reset()

        return delegate()
    finally:
        s.attr_reset()
        s.cls()
        s.goto(0, 0)
        s.cursor(True)

        s.deinit_tty()
        screen_regular()
        cursor_position_restore()


def load_data(params):
    orig_data = []
    if params.stream_mode:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            j = json.loads(line)
            orig_data.append(j)
        return orig_data
    else:
        data = sys.stdin.read()
        try:
            return json.loads(data)
        except JSONDecodeError as e:
            print("Cannot decode JSON", file=sys.stderr)
            print(e, file=sys.stderr)
            print(data, file=sys.stderr)
            sys.exit(255)


def parse_params(argv):
    params = Params()
    a = 1
    while a < len(argv):
        if sys.argv[a] == '-t':
            a += 1
            params.title = sys.argv[a]
        elif sys.argv[a] == "-s":
            params.stream_mode = True
        else:
            params.columns = json.loads(sys.argv[a])
        a += 1
    return params


def grid(state, presentation, screen_size, orig_data, column_keys) -> WGrid:
    column_titles: List[str] = [c for c in column_keys]
    column_widths: List[int] = [max_column_widths[c] for c in column_keys]

    g = WGrid(screen_size[0], screen_size[1], column_widths, column_keys,
              column_renderers(column_keys, presentation["columns"]).__getitem__,
              lambda line, column: orig_data[line].get(column_keys[column]),
              presentation.get("title"),
              column_titles)
    g.total_lines = len(orig_data)

    top_line = state["top_line"]
    if 0 <= top_line < g.total_lines:
        g.top_line = top_line

    cur_line = state["cur_line"]
    if top_line <= cur_line < g.total_lines:
        g.cur_line = cur_line

    return g


def main(g, app, pick_displayed_columns):
    # metadata = read_fd_or_default(fd=FD_METADATA_IN, default={})
    presentation = read_fd_or_default(fd=FD_PRESENTATION_IN, default={})
    state = read_fd_or_default(fd=FD_STATE_IN, default={'top_line': 0, 'cur_line': 0})
    params = parse_params(sys.argv)

    override(params, presentation)

    fd_tui = FD_TUI if fd_exists(FD_TUI) else 2
    patch_picotui(fd_tui, fd_tui)

    orig_data = load_data(params)
    infer_metadata(orig_data, presentation["columns"].__contains__)
    compute_stats(orig_data)
    infer_presentation(orig_data)

    screen_size = with_raw_terminal(read_screen_size)
    column_keys = pick_displayed_columns(screen_size[0])

    exit_code, state = run(lambda: app(g(state, presentation, screen_size, orig_data, column_keys)).run())

    write_fd_or_pass(FD_STATE_OUT, state)
    write_fd_or_pass(FD_PRESENTATION_OUT, presentation)
    if exit_code < 120:
        if (exit_code // EXIT_CODE_SHIFT) & 1 == 1:
            print(json.dumps(orig_data))
            sys.exit(exit_code)
    if exit_code != EXIT_CODE_ESCAPE:
        print(json.dumps(orig_data[state["cur_line"]]))
    sys.exit(exit_code)


def override(params, presentation):
    if params.title is not None:
        presentation["title"] = params.title
    if params.columns is not None:
        presentation["columns"] = params.columns


if __name__ == "__main__":
    main(grid, App, pick_displayed_columns)
