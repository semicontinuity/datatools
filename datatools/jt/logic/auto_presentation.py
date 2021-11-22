from math import sqrt

from datatools.jt.model.metadata import Metadata
from datatools.jt.model.presentation import ColumnRenderer, Presentation, COLORING_NONE, COLORING_HASH_ALL, \
    COLORING_HASH_FREQUENT
from datatools.util.time_bar_util import fit_time_bar

POPULATED_RATIO = 0.66


def enrich_presentation(data, metadata: Metadata, presentation: Presentation) -> Presentation:
    row_count = len(data)
    discover_columns: bool = len(presentation.columns) == 0 or should_discover_columns(presentation)
    discover_max_content_width: bool = any(c.get_renderer().max_content_width is None for c in presentation.columns.values())

    if not discover_columns and not discover_max_content_width:
        return presentation

    presentation = presentation.clone()

    if discover_columns:
        for key, column_metadata in metadata.columns.items():
            if key in presentation.columns:
                continue
            column_presentation = presentation.columns[key]
            column_presentation.title = key

            column_renderer = column_presentation.get_renderer()
            if column_renderer is None:
                column_renderer = ColumnRenderer()
                column_presentation.add_renderer(column_renderer)

            # assume that all lists are stripes for now
            if key == 'separator':
                column_renderer.separator = True
            elif column_metadata.type == 'list' and (column_metadata.stereotype == 'hashes' or column_metadata.stereotype == 'time_series'):
                column_renderer.stripes = True
            elif column_metadata.complex or column_metadata.multiline or (column_metadata.count is not None and column_metadata.count < POPULATED_RATIO * row_count):
                column_renderer.indicator = True
            else:
                column_renderer.coloring = infer_column_coloring(column_metadata, len(data))
                column_renderer.collapsed = column_metadata.contains_single_value()

    if discover_columns or discover_max_content_width:
        for record in data:
            for key, value in record.items():
                column_presentation = presentation.columns.get(key)
                if column_presentation is None:
                    continue
                column_renderer = column_presentation.get_renderer()
                if column_renderer is None:
                    column_renderer = ColumnRenderer()
                    column_presentation.add_renderer(column_renderer)
                if column_renderer.indicator:
                    continue

                # max_length might be set, but since we got here already, let's refresh it
                if column_renderer.stripes:
                    sub_presentation = column_presentation.contents
                    if sub_presentation is None:
                        column_presentation.contents = enrich_presentation(value, metadata.columns[key].metadata, Presentation())
                else:
                    value_as_string = '' if value is None else str(value)  # quick and dirty
                    column_renderer.max_content_width = max(column_renderer.max_content_width or 0, len(value_as_string))

        for key, column_metadata in metadata.columns.items():
            column_presentation = presentation.columns.get(key)
            if column_presentation is None:
                continue
            renderer = column_presentation.get_renderer()
            if renderer.stripes:
                bar, n_stripes, x_axis_amount_per_stripe = fit_time_bar(
                    column_metadata.min_value,
                    column_metadata.max_value, 100, 5)
                n_chars = (n_stripes + 5 - 1) // 5  # configure? 5 stripes/char only for SIXEL stripes
                renderer.max_content_width = 2 + n_chars
    return presentation


def should_discover_columns(presentation: Presentation):
    for column_key, column_presentation in presentation.columns.items():
        renderer = column_presentation.get_renderer()
        if renderer is None or (renderer.stripes and column_presentation.contents is None):
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
