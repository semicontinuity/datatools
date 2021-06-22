#!/usr/bin/env python3
import json

from datatools.json2ansi.app import make_json2ansi_app
from datatools.jt.app import App, main, init_from_state, default_state
from datatools.jt.auto_metadata import infer_metadata
from datatools.jt.auto_presentation import infer_presentation
from datatools.jt.exit_codes import EXIT_CODE_SHIFT, EXIT_CODE_ESCAPE, EXIT_CODE_CTRL_SPACE, EXIT_CODE_BACKSPACE, \
    EXIT_CODE_CTRL, EXIT_CODE_ALT, exit_code_key_with_modifier
from datatools.jt.ui_data import UiData
from datatools.jtng.auto_renderers import column_renderers
from datatools.jtng.grid import WGrid


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from datatools.tui.terminal import with_raw_terminal, read_screen_size


def grid(screen_size, ui_data: UiData) -> WGrid:
    column_keys, cell_renderers, row_renderers = column_renderers(ui_data.column_metadata_map, ui_data.column_presentation_map)

    def row_attrs(line):
        buffer = bytearray()
        for column_key, row_renderer in row_renderers.items():
            if line >= len(ui_data.orig_data):
                raise KeyError(line)
            buffer += row_renderer(ui_data.orig_data[line].get(column_key))
        return buffer

    def cell_value(line, column):
        if column is None:
            return None
        if type(column) is int:
            return ui_data.orig_data[line].get(column_keys[column])
        else:
            return ui_data.orig_data[line].get(column)

    g = WGrid(
        screen_size[0], screen_size[1],
        len(cell_renderers),
        cell_renderers.__getitem__,
        cell_value,
        row_attrs
    )
    g.total_lines = len(ui_data.orig_data)
    init_from_state(g, ui_data.state)
    return g


def router(app, exit_code):
    """ return new app to run or None if the just finished app won't start a new app """
    if app.app_id == 'jtng':
        if exit_code == EXIT_CODE_CTRL_SPACE:
            sub_table_column = time_series_column(app.ui_data)  # may be more than 1...
            if sub_table_column:
                return sub_table_app(app.ui_data.orig_data[app.ui_data.state["cur_line"]][sub_table_column])
            else:
                return make_json2ansi_app(app.ui_data.orig_data[app.ui_data.state["cur_line"]])
        if exit_code <= EXIT_CODE_BACKSPACE + EXIT_CODE_SHIFT + EXIT_CODE_CTRL + EXIT_CODE_ALT:  # max regular exit code
            if exit_code_key_with_modifier(exit_code, EXIT_CODE_SHIFT):
                print(json.dumps(app.ui_data.orig_data))
                return None
        if exit_code != EXIT_CODE_ESCAPE:
            print(json.dumps(app.ui_data.orig_data[app.ui_data.state["cur_line"]]))

    return None


def time_series_column(ui_data: UiData):
    for name, metadata in ui_data.column_metadata_map.items():
        if metadata.stereotype == 'time_series':
            return name


def sub_table_app(j):
    column_metadata_map = infer_metadata(j, {})
    column_presentation_map = infer_presentation(j, column_metadata_map, {})
    ui_data = UiData(j, column_metadata_map, column_presentation_map, default_state())
    screen_size = with_raw_terminal(read_screen_size)
    return App('jtng', grid(screen_size, ui_data), ui_data)


if __name__ == "__main__":
    main('jtng', App, grid, router)
