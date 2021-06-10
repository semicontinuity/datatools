from typing import Dict

from datatools.jt.auto_metadata import ColumnMetadata
from datatools.jt.auto_presentation import ColumnPresentation
from datatools.jtng.cell_renderer_colored import WColoredTextCellRenderer
from datatools.jtng.cell_renderer_indicator import WIndicatorCellRenderer
from datatools.jtng.column_state import ColumnState
from datatools.jtng.row_renderer_separator import WRowSeparatorCellRenderer


def column_renderers(column_metadata_map: Dict[str, ColumnMetadata], column_presentation_map: Dict[str, ColumnPresentation]):
    column_keys = []
    cell_renderers = []
    row_renderers = {}

    for column_key, column_presentation in column_presentation_map.items():
        column_metadata = column_metadata_map.get(column_key)

        if column_presentation.separator:
            row_renderers[column_key] = WRowSeparatorCellRenderer()
            continue

        column_keys.append(column_key)
        if column_presentation.indicator:
            cell_renderers.append(WIndicatorCellRenderer())
        else:
            cell_renderers.append(
                WColoredTextCellRenderer(
                    column_metadata,
                    column_presentation,
                    column_presentation.max_length,
                    ColumnState(column_presentation.collapsed)
                )
            )

    return column_keys, cell_renderers, row_renderers
