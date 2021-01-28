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
import os
import os.path
import signal
from json import JSONDecodeError

from typing import Dict

FD_TUI = 103

FD_METADATA_IN = 4
FD_METADATA_OUT = 5

FD_PRESENTATION_IN = 6
FD_PRESENTATION_OUT = 7

FD_STATE_IN = 8
FD_STATE_OUT = 9

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
from datatools.json.coloring import hash_code, hash_to_rgb
from datatools.tui.ansi_util import ansi_foreground_escape_code, ansi_background_escape_code


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

P_FIRST = 0
P_NONE = 1
P_STOP = 2
P_LAST = 3

KIND_SINGLE = 0
KIND_DOUBLE = 1

# for every sub-array: [vertical position * 4 + horizontal position]
# contains duplicates, but easily addressable
CHARS = [
    # vertical: single, horizontal: single
    [
        b'\xe2\x94\x8c', b'\xe2\x94\x80', b'\xe2\x94\xac', b'\xe2\x94\x90',
        b'\xe2\x94\x82', b' ', b'\xe2\x94\x82', b'\xe2\x94\x82',
        b'\xe2\x94\x9c', b'\xe2\x94\x80', b'\xe2\x94\xbc', b'\xe2\x94\xa4',
        b'\xe2\x94\x94', b'\xe2\x94\x80', b'\xe2\x94\xb4', b'\xe2\x94\x98'
    ],
    # vertical: single, horizontal: double
    [
        b'\xe2\x95\x92', b'\xe2\x95\x90', b'\xe2\x95\xa4', b'\xe2\x95\x95',
        b'\xe2\x94\x82', b' ', b'\xe2\x94\x82', b'\xe2\x94\x82',
        b'\xe2\x95\x9e', b'\xe2\x95\x90', b'\xe2\x95\xaa', b'\xe2\x95\xa1',
        b'\xe2\x95\x98', b'\xe2\x95\x90', b'\xe2\x95\xa7', b'\xe2\x95\x9b'
    ],
    # vertical: double, horizontal: single
    [
        b'\xe2\x95\x93', b'\xe2\x94\x80', b'\xe2\x95\xa5', b'\xe2\x95\xa6',
        b'\xe2\x95\x91', b' ', b'\xe2\x95\x91', b'\xe2\x95\x91',
        b'\xe2\x95\x9f', b'\xe2\x94\x80', b'\xe2\x95\xab', b'\xe2\x95\xa2',
        b'\xe2\x95\x99', b'\xe2\x94\x80', b'\xe2\x95\xa8', b'\xe2\x95\x9c'
    ],
    # vertical: double, horizontal: double
    [
        b'\xe2\x95\x94', b'\xe2\x95\x90', b'\xe2\x95\xa6', b'\xe2\x95\x97',
        b'\xe2\x95\x91', b' ', b'\xe2\x95\x91', b'\xe2\x95\x91',
        b'\xe2\x95\xa0', b'\xe2\x95\x90', b'\xe2\x95\xac', b'\xe2\x95\xa3',
        b'\xe2\x95\x9a', b'\xe2\x95\x90', b'\xe2\x95\xa9', b'\xe2\x95\x9d'
    ]
]


def draw_grid(left, top, w, h, top_kind, bottom_kind, left_kind, right_kind, h_stops, v_stops):
    def draw_line(v_pos, y, current_h_kind):
        Screen.goto(left, y)
        h_stop = 0

        border_chars = CHARS[current_h_kind]
        Screen.wr(CHARS[2 * left_kind + current_h_kind][4 * v_pos + P_FIRST])
        x = left + 1
        while True:
            next_h_stop = (w - 1, right_kind) if h_stop >= len(h_stops) else h_stops[h_stop]
            next_x = left + next_h_stop[0]
            Screen.wr(border_chars[4 * v_pos + P_NONE] * (next_x - x))
            x = next_x
            if h_stop >= len(h_stops):
                break
            else:
                next_h_stop_v_kind = next_h_stop[1]
                Screen.wr(CHARS[2 * next_h_stop_v_kind + current_h_kind][4 * v_pos + P_STOP])
                x = x + 1
                h_stop = h_stop + 1
        Screen.wr(CHARS[2 * right_kind + current_h_kind][4 * v_pos + P_LAST])

    def draw_middle():
        y = top + 1
        v_stop = 0
        while True:
            next_v_stop = (h - 1, bottom_kind) if v_stop >= len(v_stops) else v_stops[v_stop]
            next_y = top + next_v_stop[0]

            while y < next_y:
                draw_line(P_NONE, y, 0)
                y = y + 1

            if v_stop >= len(v_stops):
                break
            else:
                next_v_stop_h_kind = next_v_stop[1]
                draw_line(P_STOP, y, next_v_stop_h_kind)
                y = y + 1
                v_stop = v_stop + 1

    draw_line(P_FIRST, top, top_kind)
    draw_middle()
    draw_line(P_LAST, top + h - 1, bottom_kind)


class WGrid(Editor):
    def __init__(self, title, width, height, column_titles, column_widths, compute_cell_attrs, columns, column_keys):
        super().__init__(0, 0, width, height)
        self.compute_cell_attrs = compute_cell_attrs
        self.title = title
        self.column_titles = column_titles
        self.column_widths = self.compute_column_widths(column_widths)
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

    def set_colors(self, *c):
        if len(c) == 2:
            self.attr_color(*c)
        else:
            Screen.wr(ansi_foreground_escape_code(c[0], c[1], c[2]))
            Screen.wr(ansi_background_escape_code(c[3], c[4], c[5]))

    def compute_column_widths(self, column_widths):
        assert len(column_widths) > 0
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
            self.goto(self.x + 1, row)
            if line >= self.total_lines:
                self.show_line(None, line)
            else:
                self.show_line(self.content[line], line)
            line += 1
            row += 1

    def show_line(self, line_content, line):
        is_under_cursor = self.cur_line == line
        self.redraw_row(line_content, False, True, is_under_cursor)

    def redraw_row(self, row_items, centered, separator, is_under_cursor):
        for c in range(len(self.column_widths)):
            self.set_colors(*COLORS[ColorKey.BOX_DRAWING])
            if c > 0:
                if separator:
                    self.wr(b'\xe2\x94\x82')  # |
                else:
                    cursor_forward(1)

            column_width = self.column_widths[c]
            if row_items:
                text, text_len, attrs = render(row_items, c, self.column_keys, self.columns, self.compute_cell_attrs,
                                               column_width, is_under_cursor)
                self.set_colors(*attrs)
                if centered:
                    column_width = column_width
                    used_text_len = min(text_len, column_width)
                    before = (column_width - used_text_len) >> 1
                    self.wr(' ' * before)
                    self.wr_fixedw(text, column_width - before)
                else:
                    self.wr(text)
                    self.wr(" " * (column_width - text_len))
            else:
                self.wr(' ' * column_width)

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
max_column_widths = defaultdict(int)

orig_data = []


# TODO: if some column is not present for some rows, it should be included with smaller priority (after other columns)
def pick_displayed_columns(screen_width):
    """ Pick columns until they fit screen """
    result = []
    screen_width -= 1

    for k, v in max_column_widths.items():
        if 0 < v <= screen_width - 1 and not column_is_complex[k]:
            result.append(k)
            screen_width -= (v + 1)

    for k, v in max_column_widths.items():
        if 0 < v <= screen_width - 1 and column_is_complex[k]:
            result.append(k)
            screen_width -= (v + 1)

    return result


def render(items, column_index, column_keys, columns, compute_cell_attrs, column_width, is_under_cursor):
    column_key = column_keys[column_index]
    column_spec = columns.get(column_key)
    value = items.get(column_key)
    if column_spec is not None:
        value = value[:column_width]
        text = stripes(value, column_spec)
        attrs = COLORS[ColorKey.TEXT]
        return text, len(value), attrs
    else:
        text = str(value)
        if is_under_cursor:
            attrs = COLORS[ColorKey.CURSOR]
        else:
            attrs = compute_cell_attrs(column_index, text)
        return text, len(text), attrs


column_colorings = []


def analyze_data(data, params):
    for record in data:
        for key in record.keys():
            value = record[key]
            value_as_string = str(value)

            column_attr = column_attrs[key]
            if type(value) == dict:
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


def compute_column_coloring(column_key):
    threshold = 2 * sqrt(len(orig_data))
    nu = column_attrs[column_key].non_uniques_count
    if len(column_attrs[column_key].value_stats) < threshold:
        return COLORING_HASH_ALL
    elif nu < threshold:
        return COLORING_HASH_FREQUENT
    else:
        return COLORING_NONE


def compute_column_colorings(column_keys):
    global column_colorings
    column_colorings = [compute_column_coloring(c) for c in column_keys]


def compute_cell_attrs(column_index, text):
    color = column_colorings[column_index] if column_index < len(column_colorings) else COLORING_NONE

    text_colors = COLORS[ColorKey.TEXT]
    if color == COLORING_NONE or (
            color == COLORING_HASH_FREQUENT and column_attrs[column_keys[column_index]].value_stats[text] <= 1):
        return text_colors

    fg = hash_to_rgb(hash_code(text))
    return (fg[0], fg[1], fg[2], text_colors[3], text_colors[4], text_colors[5])


g = None


def run(params, state):
    s = Screen()
    try:
        cursor_position_save()
        screen_alt()
        s.init_tty()

        s.cls()
        s.attr_reset()

        screen_size = Screen.screen_size()

        global column_keys
        column_keys = pick_displayed_columns(screen_size[0])
        column_titles = [c for c in column_keys]
        column_widths = [max_column_widths[c] for c in column_keys]

        compute_column_colorings(column_keys)

        global g
        g = WGrid(params.title, screen_size[0], screen_size[1], column_titles, column_widths, compute_cell_attrs,
                  params.columns, column_keys)
        g.set_lines(orig_data)

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
    finally:
        s.attr_reset()
        s.cls()
        s.goto(0, 0)
        s.cursor(True)

        s.deinit_tty()
        screen_regular()
        cursor_position_restore()


def load_data(params):
    global orig_data
    if params.stream_mode:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            j = json.loads(line)
            orig_data.append(j)
    else:
        input = sys.stdin.read()
        try:
            orig_data = json.loads(input)
        except JSONDecodeError as e:
            print("Cannot decode JSON", file=sys.stderr)
            print(e, file=sys.stderr)
            print(input, file=sys.stderr)
            sys.exit(255)

    analyze_data(orig_data, params)


def read_fd_or_default(fd, default):
    try:
        with os.fdopen(fd, 'r') as f:
            return json.load(f)
    except Exception:
        return default


def write_fd_or_pass(fd, value):
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f)
    except Exception as e:
        pass


def fd_exists(fd):
    return os.path.islink(f'/proc/self/fd/{fd}')


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

    if params.title: presentation["title"] = params.title
    if params.columns: presentation["columns"] = params.columns
    return params


if __name__ == "__main__":
    presentation = read_fd_or_default(fd=FD_PRESENTATION_IN, default={})
    state = read_fd_or_default(fd=FD_STATE_IN, default={'top_line': 0, 'cur_line': 0})

    params = parse_args(sys.argv, presentation)
    fd_tui = FD_TUI if fd_exists(FD_TUI) else 2
    patch_picotui(fd_tui, fd_tui)

    load_data(params)
    signal.signal(signal.SIGWINCH, handle_sigwinch)
    exit_code, state = run(params, state)

    write_fd_or_pass(FD_STATE_OUT, state)
    write_fd_or_pass(FD_PRESENTATION_OUT, presentation)

    if exit_code < 120:
        if (exit_code // EXIT_CODE_SHIFT) & 1 == 1:
            print(json.dumps(orig_data))
            sys.exit(exit_code)

    if exit_code != EXIT_CODE_ESCAPE:
        print(json.dumps(orig_data[state["cur_line"]]))

    sys.exit(exit_code)
