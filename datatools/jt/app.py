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
from dataclasses import dataclass
from json import JSONDecodeError
from typing import List

from datatools.json.util import to_jsonisable, dataclass_from_dict
from datatools.jt.auto_metadata import enrich_metadata, Metadata
from datatools.jt.auto_presentation import enrich_presentation, Presentation
from datatools.jt.auto_renderers import column_renderers
from datatools.jt.data_bundle import DataBundle
from datatools.jt.exit_codes_mapping import *
from datatools.jt.grid import WGrid
from datatools.jt.pack_columns import pick_displayed_columns
from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import *
from datatools.tui.terminal import with_raw_terminal, read_screen_size, FD_TUI
from datatools.util.conf import write_fd_or_pass, fd_exists, FD_STATE_OUT, FD_PRESENTATION_OUT, FD_METADATA_OUT, \
    state_or_default, presentation_or_default, \
    metadata_or_default


@dataclass
class Params:
    title: str = None
    stream_mode: bool = None
    compact: bool = None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class App:
    g: WGrid
    data_bundle: DataBundle

    def __init__(self, app_id, g, data_bundle: DataBundle):
        self.app_id = app_id
        self.g = g
        self.data_bundle = data_bundle
        signal.signal(signal.SIGWINCH, self.handle_sigwinch)

    def handle_sigwinch(self, signalNumber, frame):
        screen_size = Screen.screen_size()  # not very stable, sometimes duplicate 'x1b[8' is read
        self.g.width = screen_size[0]
        self.g.height = screen_size[1]
        self.g.redraw()

    def run(self):
        res = self.g.loop()
        exit_code = KEYS_TO_EXIT_CODES.get(res)
        self.data_bundle.state = {'top_line': self.g.top_line, 'cur_line': self.g.cur_line}
        return exit_code if exit_code is not None else EXIT_CODE_ESCAPE


def load_data(params):
    return do_load_data(params)


def do_load_data(params):
    if params.stream_mode:
        orig_data = []
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
        elif sys.argv[a] == '-c':
            params.compact = True
        a += 1
    return params


def grid(screen_size, data_bundle: DataBundle) -> WGrid:
    column_keys = pick_displayed_columns(screen_size[0], data_bundle.metadata.columns, data_bundle.presentation.columns)
    column_titles: List[str] = [c for c in column_keys]
    column_widths: List[int] = [data_bundle.presentation.columns[c].max_length for c in column_keys]

    g = WGrid(
        screen_size[0], screen_size[1],
        column_widths, column_keys,
        column_renderers(column_keys, data_bundle.presentation.columns, data_bundle.metadata.columns).__getitem__,
        lambda line, column: data_bundle.orig_data[line].get(column_keys[column]),
        data_bundle.presentation.title,
        column_titles
    )
    g.total_lines = len(data_bundle.orig_data)
    init_from_state(g, data_bundle.state)
    return g


def init_from_state(g, state):
    top_line = state["top_line"]
    if 0 <= top_line < g.total_lines:
        g.top_line = top_line
    cur_line = state["cur_line"]
    if top_line <= cur_line < g.total_lines:
        g.cur_line = cur_line


def main(app_id, app_f, g, router):
    params = parse_params(sys.argv)
    orig_data = load_data(params)
    data_bundle = load_data_bundle(params, orig_data)
    fd_tui = FD_TUI if fd_exists(FD_TUI) else 2
    patch_picotui(fd_tui, fd_tui)

    screen_size = with_raw_terminal(read_screen_size)
    a = app_f(app_id, g(screen_size, data_bundle), data_bundle)
    apps_stack = []
    apps_stack.append(a)

    exit_code = 0
    while True:
        if not apps_stack:
            break
        the_app = apps_stack.pop()
        exit_code = run(the_app.run)
        new_app = router(the_app, exit_code)
        if new_app is None:
            continue
        if new_app != the_app:
            apps_stack.append(the_app)
            apps_stack.append(new_app)

    store_data_bundle(data_bundle)
    sys.exit(exit_code)


def load_data_bundle(params, orig_data):
    raw_metadata = metadata_or_default(default={})
    raw_presentation = presentation_or_default(default={})
    state = state_or_default(default=default_state())

    if len(raw_metadata) == 0 and len(raw_presentation) == 0 and params.compact:
        orig_data = [{'_': orig_data}]
    metadata = dataclass_from_dict(Metadata, raw_metadata, {'Metadata': Metadata})
    presentation = dataclass_from_dict(Presentation, raw_presentation, {'Presentation': Presentation})
    if params.title is not None:
        presentation.title = params.title

    metadata = enrich_metadata(orig_data, metadata)
    presentation = enrich_presentation(orig_data, metadata, presentation)
    return DataBundle(orig_data, metadata, presentation, state)


def store_data_bundle(data_bundle):
    write_fd_or_pass(FD_STATE_OUT, data_bundle.state)
    write_fd_or_pass(FD_PRESENTATION_OUT, to_jsonisable(data_bundle.presentation))
    write_fd_or_pass(FD_METADATA_OUT, to_jsonisable(data_bundle.metadata))


def default_state():
    return {'top_line': 0, 'cur_line': 0}


def router(app, exit_code):
    if exit_code <= EXIT_CODE_BACKSPACE + EXIT_CODE_SHIFT + EXIT_CODE_CTRL + EXIT_CODE_ALT:  # max regular exit code
        if (exit_code // EXIT_CODE_SHIFT) & 1 == 1:
            print(json.dumps(app.data_bundle.orig_data))
            return None

    if exit_code != EXIT_CODE_ESCAPE:
        print(json.dumps(app.data_bundle.orig_data[app.data_bundle.state["cur_line"]]))

    return None


if __name__ == "__main__":
    main('jt', App, grid, router)
