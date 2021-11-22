from datatools.jt.ui.classic.cell_renderer_colored import WColoredTextCellRenderer


def column_renderers(column_keys, column_presentation_map, column_metadata_map):
    renderers = []
    for i, column_key in enumerate(column_keys):
        column_presentation = column_presentation_map.get(column_key)
        # if column_presentation is not None:
        #     renderers.append(WStripesCellRenderer(column_presentation))
        # else:

        renderers.append(
            WColoredTextCellRenderer(column_metadata_map[column_key], column_presentation)
        )
    return renderers
