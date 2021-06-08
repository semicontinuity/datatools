from datatools.jt.auto_coloring import column_attrs_map
from datatools.jtng.cell_renderer_colored import WColoredTextCellRenderer


def column_renderers(column_keys, column_widths):
    column_renderers = []
    for i, column_key in enumerate(column_keys):
        column_renderers.append(WColoredTextCellRenderer(column_attrs_map[column_key], column_widths[i]))
    return column_renderers
