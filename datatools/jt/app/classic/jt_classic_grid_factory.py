from typing import List

from datatools.jt.app.classic.pack_columns import pick_displayed_columns
from datatools.jt.app.state import init_from_state
from datatools.jt.logic.auto_column_renderers import column_renderers
from datatools.jt.model.data_bundle import DataBundle
from datatools.jt.ui.classic.jt_classic_grid_base import JtClassicGridBase


def grid(screen_size, data_bundle: DataBundle) -> JtClassicGridBase:
    column_keys = pick_displayed_columns(screen_size[0], data_bundle.metadata.columns, data_bundle.presentation.columns)
    column_titles: List[str] = [c for c in column_keys]
    column_widths: List[int] = [data_bundle.presentation.columns[c].renderers[0].max_content_width for c in column_keys]

    g = JtClassicGridBase(
        0, 0,
        column_widths, column_keys,
        column_renderers(column_keys, data_bundle.presentation.columns, data_bundle.metadata.columns).__getitem__,
        lambda line, column: data_bundle.orig_data[line].get(column_keys[column]),
        data_bundle.presentation.title,
        column_titles
    )

    g.init_geometry(screen_size[0], screen_size[1])
    g.total_lines = len(data_bundle.orig_data)
    init_from_state(g, data_bundle.state)
    return g