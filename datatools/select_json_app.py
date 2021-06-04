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
import signal
from json import JSONDecodeError
from typing import Dict, List, Any, Sequence

from datatools.tui.box_drawing import draw_grid, KIND_DOUBLE, KIND_SINGLE
from datatools.tui.box_drawing_chars import V_SINGLE, V_DOUBLE
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

COLORING_NONE = "none"
COLORING_HASH_ALL = "hash-all"
COLORING_HASH_FREQUENT = "hash-frequent"

from enum import Enum
from math import sqrt

from dataclasses import dataclass
from picotui.editor import Editor

from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import *
from datatools.select_json_app_exit_codes_mapping import *
from datatools.tui.coloring import hash_code, hash_to_rgb


@dataclass
class Params:
    title: str = None
    stream_mode: bool = None
    columns = {}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def decode_rgb(s):
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


full_block = '\u2588'


def stripes(cell_contents, column_spec):
    spec_list = list(column_spec.items())
    if len(spec_list) == 1 and type(spec_list[0][1]) is dict:
        return stripes_for_nested_spec(cell_contents, spec_list[0][0], spec_list[0][1])
    else:
        return stripes_for_plain_spec(cell_contents, column_spec)


def stripes_for_plain_spec(cell_contents, column_spec):
    s = ""
    for cell in cell_contents:
        rgb_string = column_spec.get(cell)
        attr = ansi_foreground_escape_code(*decode_rgb(rgb_string) if rgb_string is not None else (255, 255, 255))
        s = s + attr + full_block
    return s


def stripes_for_nested_spec(cell_contents, field, spec):
    s = ""
    for cell in cell_contents:
        rgb_string = spec.get(cell[field])
        attr = ansi_foreground_escape_code(*decode_rgb(rgb_string) if rgb_string is not None else (255, 255, 255))
        s = s + attr + full_block
    return s


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ColorKey(Enum):
    BOX_DRAWING = 'BOX_DRAWING'
    TITLE = 'TITLE'
    COLUMN_TITLE = 'COLUMN_TITLE'
    CURSOR = 'CURSOR'
    TEXT = 'TEXT'


THEMES = {
    "mc": {
        ColorKey.BOX_DRAWING: [C_B_CYAN, C_BLUE],
        ColorKey.TITLE: [C_BLACK, C_CYAN],
        ColorKey.COLUMN_TITLE: [C_B_YELLOW, C_BLUE],
        ColorKey.CURSOR: [C_BLACK, C_CYAN],
        ColorKey.TEXT: [C_B_CYAN, C_BLUE]
    },
    "dark": {
        ColorKey.BOX_DRAWING: (64, 96, 96, 0x29, 0x0B, 0x2E),
        ColorKey.TITLE: (255, 255, 255, 24, 16, 23),
        ColorKey.COLUMN_TITLE: (255, 255, 0, 24, 16, 23),
        ColorKey.CURSOR: [C_BLACK, C_WHITE],
        ColorKey.TEXT: (255, 255, 255, 24, 16, 23)
    },
}

COLORS = THEMES["dark"]


class WGrid(Editor):
    search_str: str = ""

    def __init__(self, title, width, height, column_titles, column_widths, compute_cell_attrs, columns, column_keys, cell_renderer):
        super().__init__(0, 0, width, height)
        self.compute_cell_attrs = compute_cell_attrs
        self.title = title
        self.column_titles = column_titles
        self.column_widths = [] if len(column_titles) == 0 else self.compute_column_widths(column_widths)
        self.columns = columns
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
        self.redraw_column_titles(self.column_titles)
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

    def redraw_column_titles(self, l):
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
            self.wr(self.render_row(line, self.cur_line == line, centered=False))

            line += 1
            row += 1

    def render_row(self, line, is_under_cursor, centered):
        buffer = bytearray()

        for column_index in range(len(self.column_widths)):
            # border or separator
            buffer += set_colors_cmd_bytes(*COLORS[ColorKey.BOX_DRAWING])
            buffer += self.border_left if column_index == 0 else self.separator

            buffer1 = bytearray()
            column_width = self.column_widths[column_index]
            if line >= self.total_lines:
                append_spaces(buffer1, column_width)
            else:
                bits, used_text_len, attrs = self.cell_renderer(
                    line,
                    column_index,
                    self.columns, self.compute_cell_attrs, column_width,
                    is_under_cursor)

                if centered:
                    column_width = column_width
                    before = (column_width - used_text_len) >> 1
                    append_spaces(buffer1, before)
                    buffer1 += bits
                    append_spaces(buffer1, column_width - before - used_text_len)
                else:
                    buffer1 += bits
                    append_spaces(buffer1, column_width - used_text_len)
            buffer += buffer1

        buffer += set_colors_cmd_bytes(*COLORS[ColorKey.BOX_DRAWING]) + self.border_right
        return buffer

    def handle_mouse(self, x, y):
        pass

    def handle_cursor_keys(self, key):
        """buggy"""
        if not self.total_lines:
            return
        content_height = self.height - 3
        if key == KEY_DOWN:
            if self.cur_line + 1 != self.total_lines:
                self.cur_line += 1
                if self.cur_line >= self.top_line + self.height - 3:  # cursor went beyond visible area
                    self.top_line += 1
                    self.redraw_lines(self.top_line, content_height)
                    # scroll_region(2, 2 + content_height - 2)
                    # scroll_up()
                    # self.redraw_lines(self.top_line + content_height - 2, 2)
                else:
                    self.redraw_lines(self.cur_line - 1, 2)
        elif key == KEY_UP:
            if self.cur_line > 0:
                self.cur_line -= 1
                if self.cur_line < self.top_line:  # cursor went beyond visible area
                    self.top_line = self.cur_line
                    self.redraw_lines(self.top_line, content_height)
                    # scroll_region(3, 3 + content_height - 2)
                    # scroll_down()
                    # self.redraw_lines(self.top_line, 2)
                else:
                    self.redraw_lines(self.cur_line, 2)
        elif key == KEY_PGDN:
            if self.cur_line + 1 != self.total_lines:  # if not on the very last line
                remains = self.total_lines - (self.top_line + content_height)
                if 0 < remains:
                    delta = min(remains, content_height)
                    self.top_line += delta
                    self.cur_line = min(self.cur_line + delta,
                                        self.total_lines - 1) if delta > 0 else self.total_lines - 1
                    self.redraw_lines(self.top_line, content_height)
                else:  # everything must be visible already; must move cursor to the last line
                    self.cur_line = self.total_lines - 1
                    self.redraw_lines(self.top_line, content_height)
        elif key == KEY_PGUP:
            if self.cur_line > 0:  # if not on the very first line
                delta = min(self.top_line, content_height)
                self.top_line -= delta
                self.cur_line = max(self.cur_line - delta, 0) if delta > 0 else 0
                self.redraw_lines(self.top_line, content_height)
        else:
            return False

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
        line = self.cur_line
        while line < self.total_lines:
            for k, v in orig_data[line].items():
                if str(v).find(self.search_str) >= 0:
                    return line
            line += 1
        return None

    def set_colors(self, *c):
        if len(c) == 2:
            self.attr_color(*c)
        else:
            Screen.wr(ansi_foreground_escape_code(c[0], c[1], c[2]))
            Screen.wr(ansi_background_escape_code(c[3], c[4], c[5]))


import sys
import json
from collections import defaultdict


@dataclass
class ColumnAttrs:
    value_stats: Dict[str, int]
    non_uniques_count: int = 0


column_keys = []
column_attrs = defaultdict(lambda: ColumnAttrs(defaultdict(int)))
column_is_complex = defaultdict(bool)
unique_column_values = defaultdict(set)
max_column_widths: Dict[str, int] = defaultdict(int)

orig_data = []


# TODO: if some column is not present for some rows, it should be included with smaller priority (after other columns)
def pick_displayed_columns(screen_width) -> List[str]:
    """ Pick columns until they fit screen """
    result = []
    screen_width -= 1

    # simple columns first
    for k, v in max_column_widths.items():
        if 0 < v <= screen_width - 1 and not column_is_complex[k]:
            result.append(k)
            screen_width -= (v + 1)

    # complex columns second
    for k, v in max_column_widths.items():
        if 0 < v <= screen_width - 1 and column_is_complex[k]:
            result.append(k)
            screen_width -= (v + 1)

    return result


def render_cell_value(line, column_index, columns, compute_cell_attrs, max_width, is_under_cursor):
    column_key = column_keys[column_index]
    value = orig_data[line].get(column_key)
    column_spec = columns.get(column_key)
    if column_spec is not None:
        value = value[:max_width]
        text = stripes(value, column_spec)
        attrs = COLORS[ColorKey.TEXT]
        return set_colors_cmd_bytes(*attrs) + bytes(text, 'utf-8'), len(value), attrs
    else:
        text = str(value)
        if is_under_cursor:
            attrs = COLORS[ColorKey.CURSOR]
        else:
            attrs = compute_cell_attrs(column_index, text)
        return set_colors_cmd_bytes(*attrs) + bytes(text, 'utf-8'), len(text), attrs


column_colorings: List[str] = []


def analyze_data(data, params):
    for record in data:
        for key in record.keys():
            value = record[key]
            value_as_string = str(value)

            column_attr = column_attrs[key]
            if type(value) is dict or type(value) is list:
                column_is_complex[key] = True
            else:
                column_attr.value_stats[value_as_string] = column_attr.value_stats.get(value_as_string, 0) + 1

            cell_length = len(value) if key in params.columns else len(value_as_string)
            max_column_widths[key] = max(max_column_widths[key], cell_length)
            unique_column_values[key].add(value_as_string)

    for key, column_attr in column_attrs.items():
        for word, count in column_attr.value_stats.items():
            if count > 1:
                column_attr.non_uniques_count += 1


def compute_column_coloring(column_key: str) -> str:
    threshold = 2 * sqrt(len(orig_data))
    nu = column_attrs[column_key].non_uniques_count
    if len(column_attrs[column_key].value_stats) < threshold:
        return COLORING_HASH_ALL
    elif nu < threshold:
        return COLORING_HASH_FREQUENT
    else:
        return COLORING_NONE


def compute_column_colorings(column_keys: List[str]):
    global column_colorings
    column_colorings = [compute_column_coloring(c) for c in column_keys]


def compute_cell_attrs(column_index, text) -> Sequence[int]:
    color = column_colorings[column_index] if column_index < len(column_colorings) else COLORING_NONE

    text_colors = COLORS[ColorKey.TEXT]
    if color == COLORING_NONE or (
            color == COLORING_HASH_FREQUENT and column_attrs[column_keys[column_index]].value_stats[text] <= 1):
        return text_colors

    fg = hash_to_rgb(hash_code(text))
    return fg[0], fg[1], fg[2], text_colors[3], text_colors[4], text_colors[5]


g = None


def do_run(state, presentation, screen_size):
    global column_keys
    column_titles: List[str] = [c for c in column_keys]
    column_widths: List[int] = [max_column_widths[c] for c in column_keys]
    compute_column_colorings(column_keys)

    global g
    g = WGrid(presentation.get("title"), screen_size[0], screen_size[1], column_titles, column_widths,
              compute_cell_attrs,
              presentation["columns"], column_keys, render_cell_value)
    g.total_lines = len(orig_data)

    top_line = state["top_line"]
    if 0 <= top_line < g.total_lines:
        g.top_line = top_line

    cur_line = state["cur_line"]
    if top_line <= cur_line < g.total_lines:
        g.cur_line = cur_line

    res = g.loop()
    exit_code = KEYS_TO_EXIT_CODES.get(res)
    state = {'top_line': g.top_line, 'cur_line': g.cur_line}
    return exit_code if exit_code is not None else EXIT_CODE_ESCAPE, state


def run(code):
    s = Screen()
    try:
        cursor_position_save()
        s.init_tty()
        screen_alt()
        s.cls()
        s.attr_reset()

        return code()
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
        input = sys.stdin.read()
        try:
            return json.loads(input)
        except JSONDecodeError as e:
            print("Cannot decode JSON", file=sys.stderr)
            print(e, file=sys.stderr)
            print(input, file=sys.stderr)
            sys.exit(255)


def handle_sigwinch(signalNumber, frame):
    global g
    screen_size = Screen.screen_size()  # not very stable, sometimes duplicate 'x1b[8' is read
    g.width = screen_size[0]
    g.height = screen_size[1]
    g.redraw()


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


def main():
    presentation = read_fd_or_default(fd=FD_PRESENTATION_IN, default={})
    state = read_fd_or_default(fd=FD_STATE_IN, default={'top_line': 0, 'cur_line': 0})
    params = parse_args(sys.argv, presentation)
    fd_tui = FD_TUI if fd_exists(FD_TUI) else 2
    patch_picotui(fd_tui, fd_tui)
    global orig_data
    orig_data = load_data(params)
    analyze_data(orig_data, params)
    signal.signal(signal.SIGWINCH, handle_sigwinch)

    screen_size = with_raw_terminal(read_screen_size)
    global column_keys
    column_keys = pick_displayed_columns(screen_size[0])

    exit_code, state = run(lambda: do_run(state, presentation, screen_size))

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
