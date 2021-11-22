from typing import Dict

from datatools.jt.model.metadata import ColumnMetadata
from datatools.jt.model.presentation import ColumnPresentation
from datatools.jt.ui.ng.cell_renderer_colored import WColoredTextCellRenderer
from datatools.jt.ui.ng.cell_renderer_dict_index import WDictIndexCellRenderer
from datatools.jt.ui.ng.cell_renderer_indicator import WIndicatorCellRenderer
from datatools.jt.ui.ng.cell_renderer_stripes_hashes import WStripesHashesCellRenderer
from datatools.jt.ui.ng.cell_renderer_stripes_time_series import WTimeSeriesStripesCellRenderer
from datatools.jt.model.column_state import ColumnState
from datatools.jt.ui.ng.row_renderer_separator import WRowSeparatorCellRenderer

DICT_INDEX = 'dict-index'


def renderers(column_metadata_map: Dict[str, ColumnMetadata], column_presentation_map: Dict[str, ColumnPresentation]):
    column_keys = []
    cell_renderers = []
    row_renderers = {}

    for column_key, column_presentation in column_presentation_map.items():
        column_metadata = column_metadata_map.get(column_key)
        if column_metadata is None:
            continue
        column_renderer = column_presentation.get_renderer()
        if column_renderer and column_renderer.separator:
            row_renderers[column_key] = WRowSeparatorCellRenderer()
            continue

        column_keys.append(column_key)
        cell_renderers.append(renderer(column_metadata, column_presentation))

    return column_keys, cell_renderers, row_renderers


def renderer(column_metadata: ColumnMetadata, column_presentation: ColumnPresentation):
    column_renderer = column_presentation.get_renderer()
    if column_renderer and column_renderer.indicator:
        return WIndicatorCellRenderer(column_presentation)
    elif column_renderer.stripes:
        if column_metadata.stereotype == 'hashes':
            return WStripesHashesCellRenderer(
                column_metadata,
                column_presentation,
                column_renderer.max_content_width,
                ColumnState(column_renderer.collapsed)
            )
        elif column_metadata.stereotype == 'time_series':
            return WTimeSeriesStripesCellRenderer(
                column_metadata,
                column_presentation,
                column_renderer.max_content_width,
                ColumnState(column_renderer.collapsed)
            )
        else:
            return WIndicatorCellRenderer(column_presentation)
    else:
        if column_renderer and column_renderer.coloring == DICT_INDEX:
            return WDictIndexCellRenderer(column_metadata, column_presentation)
        else:
            return WColoredTextCellRenderer(
                column_metadata,
                column_presentation,
                column_renderer.max_content_width,
                ColumnState(column_renderer.collapsed)
            )
