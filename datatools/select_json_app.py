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
from typing import List, Any

from datatools.tui.box_drawing import draw_grid, KIND_DOUBLE, KIND_SINGLE
from datatools.tui.box_drawing_chars import V_SINGLE, V_DOUBLE
from datatools.tui.jt.grid_base import WGridBase
from datatools.tui.jt.grid_cell_renderer import WGridCellRenderer, compute_column_colorings, max_column_widths, \
    analyze_data, pick_displayed_columns
from datatools.tui.jt.themes import COLORS, ColorKey
from datatools.tui.terminal import with_raw_terminal, read_screen_size, ansi_foreground_escape_code, \
    ansi_background_escape_code, append_spaces, \
    set_colors_cmd_bytes
from datatools.util.conf import read_fd_or_default, write_fd_or_pass, fd_exists

FD_TUI = 103

FD_METADATA_IN = 104
FD_METADATA_OUT = 105

FD_PRESENTATION_IN = 106
FD_PRESENTATION_OUT = 107

FD_STATE_IN = 108
FD_STATE_OUT = 109

from dataclasses import dataclass

from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import *
from datatools.select_json_app_exit_codes_mapping import *


@dataclass
class Params:
    title: str = None
    stream_mode: bool = None
    columns = {}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class WGrid(WGridBase):
    search_str: str = ""

    def __init__(self, title, width, height, column_titles, column_widths, column_keys, cell_renderer):
        super().__init__(0, 0, width, height)
        self.title = title
        self.column_titles = column_titles
        self.column_widths = [] if len(column_titles) == 0 else self.compute_column_widths(column_widths)
        self.column_keys = column_keys

        column_positions = []
        x = 0
        for i in range(len(self.column_widths)):
            column_positions.append(x)
            x += self.column_widths[i]
            x += 1
        self.h_stops = [(x, KIND_SINGLE) for x in column_positions]
        self.h_stops = self.h_stops[1:]

        self.border_left = V_DOUBLE
        self.border_right = V_DOUBLE
        self.separator = V_SINGLE

        self.cell_renderer = cell_renderer

    def show_line(self, line_content, line):
        raise AssertionError

    def compute_column_widths(self, column_widths) -> List[Any]:
        total_width = sum(column_widths)
        budget_width = self.width - 1 - len(column_widths) - total_width
        assert budget_width >= 0
        zero_columns = sum(1 for w in column_widths if w == 0)
        if zero_columns:
            auto_width = budget_width // zero_columns
            computed_column_widths = []
            for i in range(len(column_widths)):
                if column_widths[i] != 0:
                    computed_column_widths.append(column_widths[i])
                else:
                    zero_columns -= 1
                    if zero_columns == 0:
                        computed_column_widths.append(budget_width)
                    else:
                        computed_column_widths.append(auto_width)
                        budget_width -= auto_width
        else:
            # no column has width 0, so it will be the last one
            computed_column_widths = column_widths[:]
            computed_column_widths[-1] += budget_width
        return computed_column_widths

    def redraw(self):
        self.cursor(False)
        self.redraw_grid()
        self.redraw_title()
        self.redraw_column_titles()
        self.redraw_content()

    def redraw_grid(self):
        self.set_colors(*COLORS[ColorKey.BOX_DRAWING])
        draw_grid(
            self.x, self.y, self.width, self.height,
            KIND_DOUBLE, KIND_DOUBLE, KIND_DOUBLE, KIND_DOUBLE,
            self.h_stops, []
        )

    def redraw_title(self):
        if not self.title:
            return
        max_width = self.width - 4
        used_width = min(max_width, len(self.title) + 2)
        self.goto(self.x + (self.width - used_width) / 2, self.y)
        self.set_colors(*COLORS[ColorKey.TITLE])
        self.wr_fixedw(' ' + self.title + ' ', used_width)

    def redraw_column_titles(self):
        self.goto(self.x + 1, self.y + 1)
        self.redraw_column_titles_row(self.column_titles)

    def redraw_column_titles_row(self, items):
        for c in range(len(self.column_widths)):
            self.set_colors(*COLORS[ColorKey.BOX_DRAWING])
            if c > 0:
                cursor_forward(1)

            self.set_colors(*COLORS[ColorKey.COLUMN_TITLE])
            text = items[c]
            text_len = len(text)
            column_width = self.column_widths[c]
            used_text_len = min(text_len, column_width)
            before = (column_width - used_text_len) >> 1
            self.wr(' ' * before)
            self.wr_fixedw(text, column_width - before)

    def redraw_content(self):
        self.redraw_lines(self.top_line, self.height - 3)

    def redraw_lines(self, start_line, num_lines):
        line = start_line
        row = (start_line - self.top_line) + self.y + 2  # skip border line, headers line
        for c in range(num_lines):
            self.goto(self.x, row)
            self.wr(self.render_line(line, self.cur_line == line, centered=False))
            line += 1
            row += 1

    def render_line(self, line, is_under_cursor, centered):
        buffer = bytearray()

        for column_index in range(len(self.column_widths)):
            # border or separator
            buffer += set_colors_cmd_bytes(*COLORS[ColorKey.BOX_DRAWING])
            buffer += self.border_left if column_index == 0 else self.separator

            column_width = self.column_widths[column_index]
            if line >= self.total_lines:
                append_spaces(buffer, column_width)
            else:
                buffer += self.render_cell(line, column_index, column_width, is_under_cursor, centered)

        buffer += set_colors_cmd_bytes(*COLORS[ColorKey.BOX_DRAWING]) + self.border_right
        return buffer

    def render_cell(self, line, column_index, column_width, is_under_cursor, centered):
        buffer = bytearray()
        bits, used_text_len = self.cell_renderer(line, column_index, column_width, is_under_cursor)

        if centered:
            column_width = column_width
            before = (column_width - used_text_len) >> 1
            append_spaces(buffer, before)
            buffer += bits
            append_spaces(buffer, column_width - before - used_text_len)
        else:
            buffer += bits
            append_spaces(buffer, column_width - used_text_len)

        return buffer

    def handle_edit_key(self, key):
        if key in KEYS_TO_EXIT_CODES:
            return key
        elif type(key) is bytes:
            self.search_str += key.decode("utf-8")
            line = self.search()
            if line is not None:
                content_height = self.height - 3
                if line >= self.top_line + content_height:
                    delta = line - self.cur_line
                    self.top_line += delta
                self.cur_line = line
                self.redraw_lines(self.top_line, content_height)

    def search(self):
        # line = self.cur_line
        # while line < self.total_lines:
        #     for k, v in orig_data[line].items():
        #         if str(v).find(self.search_str) >= 0:
        #             return line
        #     line += 1
        return None

    def set_colors(self, *c):
        if len(c) == 2:
            self.attr_color(*c)
        else:
            Screen.wr(ansi_foreground_escape_code(c[0], c[1], c[2]))
            Screen.wr(ansi_background_escape_code(c[3], c[4], c[5]))


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


def parse_args(argv, presentation):
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

    if params.title is not None:
        presentation["title"] = params.title
    if params.columns is not None:
        presentation["columns"] = params.columns
    return params


def grid(state, presentation, screen_size, orig_data, column_keys) -> WGrid:
    column_titles: List[str] = [c for c in column_keys]
    column_widths: List[int] = [max_column_widths[c] for c in column_keys]

    g = WGrid(
        presentation.get("title"), screen_size[0], screen_size[1], column_titles, column_widths, column_keys,
        WGridCellRenderer(presentation["columns"], compute_column_colorings(orig_data, column_keys), orig_data, column_keys)
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
    analyze_data(orig_data, params)

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
