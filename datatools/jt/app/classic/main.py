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
from typing import List

from datatools.jt.app.app_kit import Applet, main
from datatools.jt.logic.auto_column_renderers import column_renderers
from datatools.jt.model.data_bundle import DataBundle, STATE_TOP_LINE, STATE_CUR_LINE
from datatools.jt.ui.classic.grid import WGrid
from datatools.jt.app.classic.pack_columns import pick_displayed_columns


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def grid(screen_size, data_bundle: DataBundle) -> WGrid:
    column_keys = pick_displayed_columns(screen_size[0], data_bundle.metadata.columns, data_bundle.presentation.columns)
    column_titles: List[str] = [c for c in column_keys]
    column_widths: List[int] = [data_bundle.presentation.columns[c].get_renderer().max_content_width for c in column_keys]

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
    top_line = state[STATE_TOP_LINE]
    if 0 <= top_line < g.total_lines:
        g.top_line = top_line
    cur_line = state[STATE_CUR_LINE]
    if top_line <= cur_line < g.total_lines:
        g.cur_line = cur_line


def app_router(app, exit_code):
    if exit_code <= EXIT_CODE_BACKSPACE + EXIT_CODE_SHIFT + EXIT_CODE_CTRL + EXIT_CODE_ALT:  # max regular exit code
        if exit_code_key_has_modifier(exit_code, EXIT_CODE_SHIFT):
            print(json.dumps(app.data_bundle.orig_data))
            return None

    if exit_code != EXIT_CODE_ESCAPE:
        print(json.dumps(app.data_bundle.orig_data[app.data_bundle.state[STATE_CUR_LINE]]))

    return None


if __name__ == "__main__":
    main('jt', Applet, grid, app_router)
