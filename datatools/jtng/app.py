#!/usr/bin/env python3
import json

from datatools.json2ansi.app import make_json2ansi_app
from datatools.jt.app import App, main, init_from_state
from datatools.jt.exit_codes import EXIT_CODE_SHIFT, EXIT_CODE_ESCAPE, EXIT_CODE_CTRL_SPACE, EXIT_CODE_BACKSPACE, \
    EXIT_CODE_CTRL, EXIT_CODE_ALT, exit_code_key_with_modifier
from datatools.jtng.auto_renderers import column_renderers
from datatools.jtng.grid import WGrid
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from datatools.tui.picotui_util import run


def grid(state, presentation, screen_size, orig_data, column_metadata_map, column_presentation_map) -> WGrid:
    column_keys, cell_renderers, row_renderers = column_renderers(column_metadata_map, column_presentation_map)

    def row_attrs(line):
        buffer = bytearray()
        for column_key, row_renderer in row_renderers.items():
            if line >= len(orig_data):
                raise KeyError(line)
            buffer += row_renderer(orig_data[line].get(column_key))
        return buffer

    def cell_value(line, column):
        if column is None:
            return None
        if type(column) is int:
            return orig_data[line].get(column_keys[column])
        else:
            return orig_data[line].get(column)

    g = WGrid(
        screen_size[0], screen_size[1],
        len(cell_renderers),
        cell_renderers.__getitem__,
        cell_value,
        row_attrs
    )
    g.total_lines = len(orig_data)
    init_from_state(g, state)
    return g


def finalizer(exit_code, orig_data, state):
    """ return True to signal that the application loop must be terminated """
    if exit_code == EXIT_CODE_CTRL_SPACE:
        run(lambda: make_json2ansi_app(orig_data[state["cur_line"]]).run())
        return False
    if exit_code < EXIT_CODE_BACKSPACE + EXIT_CODE_SHIFT + EXIT_CODE_CTRL + EXIT_CODE_ALT:  # max regular exit code
        if exit_code_key_with_modifier(exit_code, EXIT_CODE_SHIFT):
            print(json.dumps(orig_data))
            return True
    if exit_code != EXIT_CODE_ESCAPE:
        print(json.dumps(orig_data[state["cur_line"]]))

    return True


if __name__ == "__main__":
    main(grid, App, finalizer)
