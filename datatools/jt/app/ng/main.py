#!/usr/bin/env python3
import json

from datatools.json2ansi.app import make_json2ansi_applet
from datatools.json2ansi.default_style import default_style
from datatools.jt.app.app_kit import Applet, main, default_state
from datatools.jt.app.classic.main import init_from_state
from datatools.jt.model.exit_codes import *
from datatools.jt.logic.auto_metadata import enrich_metadata
from datatools.jt.logic.auto_presentation import enrich_presentation
from datatools.jt.logic.auto_renderers import renderers
from datatools.jt.model.data_bundle import DataBundle, STATE_CUR_LINE, STATE_CUR_LINE_Y
from datatools.jt.model.metadata import Metadata
from datatools.jt.model.presentation import Presentation
from datatools.jt.ui.ng.grid import WGrid
from datatools.tui.terminal import with_raw_terminal, read_screen_size

LEAF_CONTENTS_APPLET_STYLE = default_style([48, 40, 24])


def grid(screen_size, data_bundle: DataBundle) -> WGrid:
    column_keys, cell_renderers, row_renderers = renderers(data_bundle.metadata.columns, data_bundle.presentation.columns)

    def row_attrs(line):
        attrs = 0
        for column_key, row_renderer in row_renderers.items():
            attrs |= row_renderer(data_bundle.orig_data[line].get(column_key))
        return attrs

    def cell_value(line, column):
        if column is None:
            return None
        if type(column) is int:
            return data_bundle.orig_data[line].get(column_keys[column])
        else:
            return data_bundle.orig_data[line].get(column)

    g = WGrid(
        screen_size[0], screen_size[1],
        len(cell_renderers),
        cell_renderers.__getitem__,
        cell_value,
        row_attrs
    )
    g.total_lines = len(data_bundle.orig_data)
    init_from_state(g, data_bundle.state)
    return g


def app_router(applet, exit_code):
    """ return new app to run or None if the just finished app won't start a new app """
    if applet.app_id == 'jtng':
        if exit_code == EXIT_CODE_CTRL_SPACE:
            sub_table_column = time_series_column(applet.data_bundle)  # may be more than 1...
            if sub_table_column:
                return nested_table_applet(
                    applet.data_bundle.orig_data[applet.data_bundle.state[STATE_CUR_LINE]][sub_table_column],
                    applet.data_bundle.metadata.columns[sub_table_column].metadata,
                    applet.data_bundle.presentation.columns[sub_table_column].contents)
            else:
                return make_json2ansi_applet(
                    applet.data_bundle.orig_data[applet.data_bundle.state[STATE_CUR_LINE]],
                    LEAF_CONTENTS_APPLET_STYLE,
                    {"anchor": {"x": 0, "y": (applet.data_bundle.state.get(STATE_CUR_LINE_Y))}},
                    True
                )
        if exit_code <= EXIT_CODE_MAX_REGULAR:
            if exit_code_key_has_modifier(exit_code, EXIT_CODE_SHIFT):
                print(json.dumps(applet.data_bundle.orig_data))
                return None
        if exit_code != EXIT_CODE_ESCAPE:
            print(json.dumps(applet.data_bundle.orig_data[applet.data_bundle.state[STATE_CUR_LINE]]))

    return None


def time_series_column(data_bundle: DataBundle):
    for name, metadata in data_bundle.metadata.columns.items():
        if metadata.stereotype == 'time_series':
            return name


def nested_table_applet(cell_j, column_contents_metadata: Metadata, column_contents_presentation: Presentation) -> Applet:
    metadata = enrich_metadata(cell_j, column_contents_metadata or Metadata())
    presentation = enrich_presentation(cell_j, metadata, column_contents_presentation or Presentation())

    data_bundle = DataBundle(cell_j, metadata, presentation, default_state())
    screen_size = with_raw_terminal(read_screen_size)
    return Applet('jtng', grid(screen_size, data_bundle), data_bundle)


if __name__ == "__main__":
    main('jtng', Applet, grid, app_router)
