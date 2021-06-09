from datatools.jtng.cell_renderer_colored import WColoredTextCellRenderer
from datatools.jtng.column_state import ColumnState


def column_renderers(column_keys, column_widths, column_metadata_map, column_presentation_map):
    column_renderers = []
    for i, column_key in enumerate(column_keys):
        column_metadata = column_metadata_map.get(column_key)
        column_presentation = column_presentation_map.get(column_key)
        column_renderers.append(
            WColoredTextCellRenderer(
                column_metadata,
                column_presentation,
                column_widths[i],
                ColumnState(column_metadata is None or column_metadata.contains_single_value())
            )
        )

    return column_renderers
