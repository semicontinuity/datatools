#!/usr/bin/env python3
import json

from datatools.json.util import to_jsonisable
from datatools.json2ansi.app import make_json2ansi_applet
from datatools.json2ansi_toolkit.default_style import default_style
from datatools.jt.app.app_kit import Applet, app_kit_main
from datatools.jt.app.state import default_state
from datatools.jt.app.ng.grid_factory import grid, do_make_grid
from datatools.jt.app.ng.jt_ng_grid import JtNgGrid
from datatools.jt.logic.auto_metadata import enrich_metadata
from datatools.jt.logic.auto_presentation import enrich_presentation
from datatools.jt.logic.auto_values_info import compute_column_values_info
from datatools.jt.model.data_bundle import DataBundle, STATE_CUR_LINE, STATE_CUR_LINE_Y, STATE_CUR_CELL_VALUE, \
    STATE_CUR_COLUMN_KEY
from datatools.jt.model.exit_codes import *
from datatools.jt.model.metadata import Metadata, STEREOTYPE_TIME_SERIES
from datatools.jt.model.presentation import Presentation
from datatools.jt.ui.ng.cell_renderer_indicator import WIndicatorCellRenderer
from datatools.jt2h.app import page_node_auto, page_node_basic_auto, md_table_node
from datatools.jt2h.app_json_page import page_node, md_node
from datatools.tui.terminal import with_raw_terminal, read_screen_size
from datatools.util.object_exporter import init_object_exporter

LEAF_CONTENTS_APPLET_STYLE = default_style([48, 40, 24])


def filter_non_collapsed(r: dict, collapsed: dict[str, bool]):
    return {k: v for k, v in r.items() if not collapsed.get(k)}


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
        elif exit_code == EXIT_CODE_ENTER + EXIT_CODE_ALT:
            # Alt+Enter: Exit and dump current cell WITH COLUMN NAME as JSON
            print(json.dumps(
                {applet.data_bundle.state[STATE_CUR_COLUMN_KEY]: applet.data_bundle.state[STATE_CUR_CELL_VALUE]}))
            return None

        elif exit_code == EXIT_CODE_F12:
            # F12: Exit and dump table contents as basic HTML
            collapsed = collapsed_columns(applet)
            j = applet.data_bundle.orig_data
            print(page_node_basic_auto([filter_non_collapsed(r, collapsed) for r in j]))
            return None
        elif exit_code == EXIT_CODE_F12 + EXIT_CODE_CTRL:
            # Ctrl+F12: Exit and dump table contents as HTML with JS
            print(page_node_auto(applet.data_bundle.orig_data))
            return None
        elif exit_code == EXIT_CODE_F12 + EXIT_CODE_SHIFT:
            # Shift+F12: Exit and dump table contents as HTML for insertion into markdown
            j = applet.data_bundle.orig_data
            print(md_table_node(j))
            return None

        elif exit_code == EXIT_CODE_F12 + EXIT_CODE_ALT:
            # Alt+F12: Exit and dump cell contents as HTML
            print(page_node(applet.data_bundle.state[STATE_CUR_CELL_VALUE]))
            return None
        elif exit_code == EXIT_CODE_F12 + EXIT_CODE_ALT + EXIT_CODE_SHIFT:
            # Alt+Shift+F12: Exit and dump cell contents as HTML for markdown
            print(md_node(applet.data_bundle.state[STATE_CUR_CELL_VALUE]))
            return None

        elif exit_code == EXIT_CODE_F10 + EXIT_CODE_CTRL:
            print(json.dumps(to_jsonisable(applet.data_bundle.presentation)))
            return None

        elif exit_code <= EXIT_CODE_MAX_REGULAR:
            # Any other key with Shift?: Dump document as JSON
            if exit_code_key_has_modifier(exit_code, EXIT_CODE_SHIFT):
                print(json.dumps(applet.data_bundle.orig_data))
                return None

        if exit_code != EXIT_CODE_ESCAPE:
            # Dump current line as JSON
            print(json.dumps(applet.data_bundle.orig_data[applet.data_bundle.state[STATE_CUR_LINE]]))

    return None


def collapsed_columns(applet):
    collapsed = {}
    for i in range(applet.g.column_count):
        r = applet.g.column_cell_renderer_f(i).delegate()
        collapsed[r.render_data.column_key] = type(r) == WIndicatorCellRenderer
    return collapsed


def time_series_column(data_bundle: DataBundle):
    for name, metadata in data_bundle.metadata.columns.items():
        if metadata.stereotype == STEREOTYPE_TIME_SERIES:
            return name


def nested_table_applet(cell_j, column_contents_metadata: Metadata,
                        column_contents_presentation: Presentation) -> Applet:
    values_info = compute_column_values_info(cell_j, column_contents_metadata or Metadata())
    metadata = enrich_metadata(cell_j, column_contents_metadata or Metadata())
    presentation = enrich_presentation(cell_j, values_info, metadata, column_contents_presentation or Presentation())

    data_bundle = DataBundle(cell_j, values_info, metadata, presentation, default_state())
    screen_size = with_raw_terminal(read_screen_size)
    return Applet('jtng', grid(do_make_grid(data_bundle, JtNgGrid), screen_size, data_bundle), data_bundle)


if __name__ == "__main__":
    # sleep(1.1)

    # var = get_pipe_peer_env_var('PRODUCES_ENTP', 0)
    # if var is not None:
    #     while True:
    #         line = sys.stdin.readline()
    #         if not line or len(line) == 0 or line == '\n':
    #             break
    #         print(line.removesuffix('\n'))

    init_object_exporter()
    app_kit_main('jtng', Applet, grid, app_router)
