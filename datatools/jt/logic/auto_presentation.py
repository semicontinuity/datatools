from math import sqrt

from datatools.jt.model.metadata import Metadata, STEREOTYPE_TIME_SERIES
from datatools.jt.model.presentation import Presentation, COLORING_NONE, COLORING_HASH_ALL, COLORING_HASH_FREQUENT
from datatools.jt.ui.ng.cell_renderer_colored import ColumnRendererColoredPlain, ColumnRendererColoredHash, \
    ColumnRendererColoredMapping
from datatools.jt.ui.ng.cell_renderer_indicator import ColumnRendererIndicator
from datatools.jt.ui.ng.cell_renderer_stripes_hashes import ColumnRendererStripesHashColored
from datatools.jt.ui.ng.cell_renderer_stripes_time_series import ColumnRendererStripesTimeSeries
from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.util.time_bar_util import fit_time_bar

POPULATED_RATIO = 0.66


def enrich_presentation(data, metadata: Metadata, presentation: Presentation) -> Presentation:
    row_count = len(data)
    discover_columns: bool = len(presentation.columns) == 0 or should_discover_columns(presentation)
    discover_max_content_width: bool = any(r.max_content_width is None for c in presentation.columns.values() for r in c.renderers)

    if not discover_columns and not discover_max_content_width:
        return presentation

    presentation = presentation.clone()

    if discover_columns:
        for key, column_metadata in metadata.columns.items():
            if key in presentation.columns:
                continue
            column_presentation = presentation.columns[key]
            column_presentation.title = key

            if key == 'separator':
                column_presentation.separator = True
                continue

            if column_metadata.type == 'list' and (column_metadata.stereotype == 'hashes' or column_metadata.stereotype == STEREOTYPE_TIME_SERIES):
                # assume that all lists are stripes for now
                if column_metadata.stereotype == 'hashes':
                    column_renderer = ColumnRendererStripesHashColored()
                elif column_metadata.stereotype == STEREOTYPE_TIME_SERIES:
                    column_renderer = ColumnRendererStripesTimeSeries()
                else:
                    column_renderer = ColumnRendererIndicator()
                column_presentation.add_renderer(column_renderer)
            elif column_metadata.complex or column_metadata.multiline or (column_metadata.count is not None and column_metadata.count < POPULATED_RATIO * row_count):
                column_presentation.add_renderer(ColumnRendererIndicator())
            else:
                coloring = infer_column_coloring(column_metadata, len(data))
                if coloring == COLORING_NONE or key == metadata.timestamp_field:
                    column_presentation.add_renderer(ColumnRendererColoredPlain())
                    column_presentation.add_renderer(ColumnRendererIndicator())
                else:
                    column_renderer = ColumnRendererColoredHash()
                    column_renderer.color = coloring
                    indicator = ColumnRendererIndicator()
                    if column_metadata.contains_single_value():
                        color = '#' + "%02X%02X%02X" % hash_to_rgb(hash_code(column_presentation.title), offset=64)
                        indicator.color = color
                        column_renderer.color = color
                        column_presentation.add_renderer(indicator)
                        column_presentation.add_renderer(column_renderer)
                    else:
                        column_presentation.add_renderer(column_renderer)
                        column_presentation.add_renderer(indicator)

    if discover_columns or discover_max_content_width:
        for record in data:
            for key, value in record.items():
                column_presentation = presentation.columns.get(key)
                if column_presentation is None or column_presentation.separator:
                    continue

                for column_renderer in column_presentation.renderers:
                    # max_length might be set, but since we got here already, let's refresh it
                    if type(column_renderer) is ColumnRendererStripesTimeSeries:
                        sub_presentation = column_presentation.contents
                        if sub_presentation is None:
                            column_presentation.contents = enrich_presentation(value, metadata.columns[key].metadata, Presentation())
                    else:
                        if type(column_renderer) is ColumnRendererColoredPlain or type(column_renderer) is ColumnRendererColoredHash or type(column_renderer) is ColumnRendererColoredMapping:
                            value_as_string = '' if value is None else str(value)  # quick and dirty
                            column_renderer.max_content_width = max(column_renderer.max_content_width or 0, len(value_as_string))

        for key, column_metadata in metadata.columns.items():
            column_presentation = presentation.columns.get(key)
            if column_presentation is None:
                continue

            for column_renderer in column_presentation.renderers:
                if type(column_renderer) is ColumnRendererStripesTimeSeries:
                    bar, n_stripes, x_axis_amount_per_stripe = fit_time_bar(
                        column_metadata.min_value,
                        column_metadata.max_value, 100, 5)
                    n_chars = (n_stripes + 5 - 1) // 5  # configure? 5 stripes/char only for SIXEL stripes
                    column_renderer.max_content_width = 2 + n_chars
    return presentation


def should_discover_columns(presentation: Presentation):
    for column_key, column_presentation in presentation.columns.items():
        for column_renderer in column_presentation.renderers:
            if type(column_renderer) is ColumnRendererStripesTimeSeries and column_presentation.contents is None:
                return True
    return False


def infer_column_coloring(column_metadata, records_count) -> str:
    threshold = 2 * sqrt(records_count)
    if len(column_metadata.unique_values) + len(column_metadata.non_unique_value_counts) < threshold:
        return COLORING_HASH_ALL
    elif len(column_metadata.non_unique_value_counts) < threshold:
        return COLORING_HASH_FREQUENT
    else:
        return COLORING_NONE
