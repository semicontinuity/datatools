from datatools.jt.app.app_kit import init_from_state
from datatools.jt.logic.auto_renderers import make_renderers
from datatools.jt.model.data_bundle import DataBundle
from datatools.jt.ui.ng.grid import JtNgGridBase


def grid(grid_f, screen_size, data_bundle: DataBundle) -> JtNgGridBase:
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

    g: JtNgGridBase = grid_f(
        0, 0,
        len(cell_renderers),
        lambda i: cell_renderers[i],
        lambda line, index: None if index is None else named_cell_value(line, column_keys[index]),
        row_attrs,
        data_bundle,
        column_keys
    )
    g.init_geometry(screen_size[0], screen_size[1])
    g.layout()
    g.total_lines = len(data_bundle.orig_data)

    init_from_state(g, data_bundle.state)
    return g