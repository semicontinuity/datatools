from datatools.jt.cell_renderer_colored import WColoredTextCellRenderer
from datatools.jt.cell_renderer_stripes import WStripesCellRenderer


def column_renderers(column_keys, column_presentation_map, column_metadata_map):
    column_renderers = []
    for i, column_key in enumerate(column_keys):
        column_presentation = column_presentation_map.get(column_key)
        # if column_presentation is not None:
        #     column_renderers.append(WStripesCellRenderer(column_presentation))
        # else:

        column_renderers.append(
            WColoredTextCellRenderer(column_metadata_map[column_key], column_presentation)
        )
    return column_renderers
