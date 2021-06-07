from datatools.jt.auto_coloring import column_attrs_map
from datatools.jt.cell_renderer_colored import WColoredTextCellRenderer
from datatools.jt.cell_renderer_stripes import WStripesCellRenderer


def column_renderers(column_keys, columns_presentation):
    column_renderers = []
    for i, column_key in enumerate(column_keys):
        column_spec = columns_presentation.get(column_key)
        if column_spec is not None:
            column_renderers.append(WStripesCellRenderer(column_spec))
        else:
            column_renderers.append(
                WColoredTextCellRenderer(column_attrs_map[column_key])
            )
    return column_renderers
