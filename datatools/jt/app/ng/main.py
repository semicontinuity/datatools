#!/usr/bin/env python3
import json

from datatools.json2ansi.app import make_json2ansi_applet
from datatools.json2ansi_toolkit.default_style import default_style
from datatools.jt.app.app_kit import Applet, app_kit_main, default_state, init_from_state
from datatools.jt.logic.auto_metadata import enrich_metadata
from datatools.jt.logic.auto_presentation import enrich_presentation
from datatools.jt.logic.auto_renderers import make_renderers
from datatools.jt.logic.auto_values_info import compute_column_values_info
from datatools.jt.model.data_bundle import DataBundle, STATE_CUR_LINE, STATE_CUR_LINE_Y, STATE_CUR_CELL_VALUE, \
    STATE_CUR_COLUMN_KEY
from datatools.jt.model.exit_codes import *
from datatools.jt.model.metadata import Metadata, STEREOTYPE_TIME_SERIES
from datatools.jt.model.presentation import Presentation
from datatools.jt.ui.ng.grid import WGrid
from datatools.jt2h.app import page_node_auto, column_renderers_auto, page_node_basic_auto
from datatools.jt2h.log_node import LogNode
from datatools.jt2h.page_node_css import PAGE_NODE_CSS, TABLE_NODE_CSS
from datatools.tui.terminal import with_raw_terminal, read_screen_size
from datatools.util.object_exporter import init_object_exporter
from util.html.elements import style
from util.html.md_html_node import MdHtmlNode

LEAF_CONTENTS_APPLET_STYLE = default_style([48, 40, 24])


def grid(screen_size, data_bundle: DataBundle) -> WGrid:
    def named_cell_value(line, column_key):
        if column_key is None:
            return None
        return data_bundle.orig_data[line].get(column_key)

    column_keys, cell_renderers, row_renderers = make_renderers(
        data_bundle.values_stats.columns,
        data_bundle.metadata.columns,
        data_bundle.presentation.columns,
        named_cell_value,
        len(data_bundle.orig_data)
    )

    def row_attrs(line):
        attrs = 0
        for column_key, row_renderer in row_renderers.items():
            attrs |= row_renderer(data_bundle.orig_data[line].get(column_key))
        return attrs

    g = WGrid(
        screen_size[0], screen_size[1],
        len(cell_renderers),
        lambda i: cell_renderers[i],
        lambda line, index: None if index is None else named_cell_value(line, column_keys[index]),
        row_attrs,
        data_bundle,
        column_keys
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
        elif exit_code == EXIT_CODE_ENTER + EXIT_CODE_ALT:
            # Alt+Enter: Exit and dump current cell as JSON
            print(json.dumps(
                {applet.data_bundle.state[STATE_CUR_COLUMN_KEY]: applet.data_bundle.state[STATE_CUR_CELL_VALUE]}))
            return None
        elif exit_code == EXIT_CODE_F12 + EXIT_CODE_CTRL:
            # F12: Exit and dump table contents as HTML with JS
            print(page_node_auto(applet.data_bundle.orig_data))
            return None
        elif exit_code == EXIT_CODE_F12 + EXIT_CODE_ALT:
            # F12: Exit and dump table contents as basic HTML
            j = applet.data_bundle.orig_data
            print(page_node_basic_auto(j))
            return None
        elif exit_code == EXIT_CODE_F12 + EXIT_CODE_ALT + EXIT_CODE_SHIFT:
            # F12: Exit and dump table contents as HTML for insertion into markdown
            j = applet.data_bundle.orig_data
            print(
                MdHtmlNode(
                    style(
                        TABLE_NODE_CSS,
                        LogNode.CSS_CORE
                    ),
                    LogNode(j, column_renderers_auto(j), dynamic_columns=False, dynamic_rows=False)
                )
            )
            return None
        elif exit_code <= EXIT_CODE_MAX_REGULAR:
            # Any other key: Dump document as JSON
            if exit_code_key_has_modifier(exit_code, EXIT_CODE_SHIFT):
                print(json.dumps(applet.data_bundle.orig_data))
                return None

        if exit_code != EXIT_CODE_ESCAPE:
            # Dump current line as JSON
            print(json.dumps(applet.data_bundle.orig_data[applet.data_bundle.state[STATE_CUR_LINE]]))

    return None


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
    return Applet('jtng', grid(screen_size, data_bundle), data_bundle)


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
