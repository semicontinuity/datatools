from datatools.jt.auto_coloring import column_attrs_map
from datatools.jtng.cell_renderer_colored import WColoredTextCellRenderer
from datatools.jtng.column_state import ColumnState


def column_renderers(column_keys, column_widths):
    column_renderers = []
    for i, column_key in enumerate(column_keys):
        column_attrs = column_attrs_map.get(column_key)
        column_renderers.append(
            WColoredTextCellRenderer(
                column_attrs, column_widths[i], ColumnState(column_attrs is None or column_attrs.contains_single_value())
            )
        )

    return column_renderers
