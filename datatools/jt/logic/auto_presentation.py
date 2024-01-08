from math import sqrt

from datatools.jt.model.metadata import Metadata, STEREOTYPE_TIME_SERIES, ColumnMetadata
from datatools.jt.model.presentation import Presentation, COLORING_NONE, COLORING_HASH_ALL, COLORING_HASH_FREQUENT
from datatools.jt.model.values_info import ColumnsValuesInfo, ValuesInfo
from datatools.jt.ui.ng.cell_renderer_colored import ColumnRendererColoredPlain, ColumnRendererColoredHash, \
    ColumnRendererColoredMapping
from datatools.jt.ui.ng.cell_renderer_indicator import ColumnRendererIndicator
from datatools.jt.ui.ng.cell_renderer_stripes_hashes import ColumnRendererStripesHashColored
from datatools.jt.ui.ng.cell_renderer_stripes_time_series import ColumnRendererStripesTimeSeries
from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.util.logging import debug
from datatools.util.time_bar_util import fit_time_bar

POPULATED_RATIO = 0.66


def enrich_presentation(data, values_info: ColumnsValuesInfo, metadata: Metadata, presentation: Presentation) -> Presentation:
    row_count = len(data)
    discover_columns: bool = len(presentation.columns) == 0 or should_discover_columns(presentation)
    discover_max_content_width: bool = any(r.max_content_width is None for c in presentation.columns.values() for r in c.renderers)

    debug('enrich_presentation', discover_columns=discover_columns)
    debug('discover_max_content_width', discover_max_content_width=discover_max_content_width)

    if not discover_columns and not discover_max_content_width:
        return presentation

    presentation = presentation.clone()

    if discover_columns:
        do_discover_columns(data, values_info, metadata, presentation, row_count)
    if discover_columns or discover_max_content_width:
        scan(data, metadata, presentation)
        post_scan_analysis(metadata, presentation)

    return presentation


def do_discover_columns(data, values_info: ColumnsValuesInfo, metadata, presentation, row_count):
    for key, column_metadata in metadata.columns.items():
        if key in presentation.columns:
            continue
        debug('do_discover_columns', key=key)
        column_values_info = values_info.columns[key]
        column_presentation = presentation.columns[key]
        column_presentation.title = key

        if key == 'separator':
            column_presentation.separator = True
            continue

        if column_metadata.type == 'list' and (
                column_metadata.stereotype == 'hashes' or column_metadata.stereotype == STEREOTYPE_TIME_SERIES):
            # assume that all lists are stripes for now
            if column_metadata.stereotype == 'hashes':
                column_renderer = ColumnRendererStripesHashColored()
            elif column_metadata.stereotype == STEREOTYPE_TIME_SERIES:
                column_renderer = ColumnRendererStripesTimeSeries()
            else:
                column_renderer = ColumnRendererIndicator(thick=True)
            column_presentation.add_renderer(column_renderer)
        elif column_metadata.complex or column_metadata.multiline or (
                column_values_info.count is not None and column_values_info.count < POPULATED_RATIO * row_count):
            column_presentation.add_renderer(ColumnRendererIndicator(thick=True))
        else:
            coloring = infer_column_coloring(column_values_info, len(data))
            if coloring == COLORING_NONE or key == metadata.timestamp_field:
                plain_renderer = ColumnRendererColoredPlain()
                plain_renderer.color = '#' + "%02X%02X%02X" % hash_to_rgb(hash_code(column_presentation.title),
                                                                          offset=160)
                column_presentation.add_renderer(plain_renderer)

                renderer_indicator = ColumnRendererIndicator()
                renderer_indicator.color = '#' + "%02X%02X%02X" % hash_to_rgb(hash_code(column_presentation.title),
                                                                              offset=64)
                column_presentation.add_renderer(renderer_indicator)
            else:
                column_renderer = ColumnRendererColoredHash()
                if coloring == COLORING_HASH_FREQUENT:
                    column_renderer.onlyFrequent = True
                    column_renderer.color = '#' + "%02X%02X%02X" % hash_to_rgb(hash_code(column_presentation.title), offset=160)
                else:
                    column_renderer.color = coloring

                indicator = ColumnRendererIndicator()
                indicator.color = '#' + "%02X%02X%02X" % hash_to_rgb(hash_code(column_presentation.title), offset=64)
                if column_values_info.contains_single_value():
                    column_presentation.add_renderer(indicator)
                    column_presentation.add_renderer(column_renderer)
                else:
                    column_presentation.add_renderer(column_renderer)
                    column_presentation.add_renderer(indicator)


def scan(data, metadata, presentation):
    debug('scan')
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
                    if type(column_renderer) is ColumnRendererColoredPlain or \
                            type(column_renderer) is ColumnRendererColoredHash or \
                            type(column_renderer) is ColumnRendererColoredMapping:
                        value_as_string = '' if value is None else str(value)  # quick and dirty
                        column_renderer.max_content_width = max(column_renderer.max_content_width or 0,
                                                                len(value_as_string))


def post_scan_analysis(metadata, presentation):
    for key, column_metadata in metadata.columns.items():
        debug('post_scan_analysis', key=key)
        column_presentation = presentation.columns.get(key)
        if column_presentation is None:
            debug('post_scan_analysis', column_presentation=column_presentation)
            continue

        for column_renderer in column_presentation.renderers:
            debug('post_scan_analysis', column_renderer=column_renderer)
            if type(column_renderer) is ColumnRendererStripesTimeSeries:
                debug('post_scan_analysis', min_value=column_metadata.min_value, max_value=column_metadata.max_value)
                bar, n_stripes, x_axis_amount_per_stripe = fit_time_bar(
                    column_metadata.min_value,
                    column_metadata.max_value, 100, 5)
                n_chars = (n_stripes + 5 - 1) // 5  # configure? 5 stripes/char only for SIXEL stripes
                column_renderer.max_content_width = 2 + n_chars


def should_discover_columns(presentation: Presentation):
    debug('should_discover_columns')
    for column_key, column_presentation in presentation.columns.items():
        for column_renderer in column_presentation.renderers:
            debug('should_discover_columns', column_renderer_type=str(type(column_renderer).__name__))
            if type(column_renderer) is ColumnRendererStripesTimeSeries:
                debug('should_discover_columns', column_presentation_contents=column_presentation.contents)
                if column_presentation.contents is None:
                    return True
    return False


def infer_column_coloring(column_metadata: ValuesInfo, records_count: int) -> str:
    threshold = 2 * sqrt(records_count)
    debug('infer_column_coloring', records_count=records_count, threshold=threshold, unique_values=len(column_metadata.unique_values), non_unique_value_counts=len(column_metadata.non_unique_value_counts))
    # if len(column_attr.non_unique_value_counts) == 0 or (len(column_attr.unique_values) == 0 and len(column_attr.non_unique_value_counts) == 1):
    if len(column_metadata.unique_values) == records_count:
        return COLORING_NONE
    elif len(column_metadata.unique_values) + len(column_metadata.non_unique_value_counts) < threshold:
        return COLORING_HASH_ALL
    elif 0 < len(column_metadata.non_unique_value_counts) < threshold:
        return COLORING_HASH_FREQUENT
    else:
        return COLORING_NONE
