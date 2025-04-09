from math import sqrt

from datatools.jt.logic.auto_values_info import single_key_of_dict
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
    debug('enrich_presentation', values_info_columns=list(values_info.columns))
    row_count = len(data)
    discover_columns: bool = len(presentation.columns) == 0 or should_discover_columns(presentation)
    discover_max_content_width: bool = any(r.max_content_width is None for c in presentation.columns.values() for r in c.renderers)

    debug('enrich_presentation', discover_columns=discover_columns)
    debug('discover_max_content_width', discover_max_content_width=discover_max_content_width)

    if not discover_columns and not discover_max_content_width:
        return presentation

    debug('enrich_presentation', clone_presentation=True)
    presentation = presentation.clone()

    if discover_columns:
        do_discover_columns(data, values_info, metadata, presentation, row_count)
    if discover_columns or discover_max_content_width:
        enhance_column_presentation_renderers(data, values_info, metadata, presentation)
        post_scan_analysis(metadata, presentation)

    return presentation


def do_discover_columns(data, values_info: ColumnsValuesInfo, metadata, presentation, row_count):
    debug('do_discover_columns', values_info_columns=list(values_info.columns))
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
                renderer_main = ColumnRendererStripesHashColored()
            elif column_metadata.stereotype == STEREOTYPE_TIME_SERIES:
                renderer_main = ColumnRendererStripesTimeSeries()
            else:
                renderer_main = ColumnRendererIndicator(thick=True)
            column_presentation.add_renderer(renderer_main)
        else:
            complex = column_metadata.complex and not column_metadata.has_one_dict_key
            multiline = column_metadata.multiline
            # sparse = column_values_info.count is not None and column_values_info.count < POPULATED_RATIO * row_count
            # if complex or multiline or sparse:
            if complex or multiline:
                debug('do_discover_columns', complex=complex, multiline=multiline)
                column_presentation.add_renderer(ColumnRendererIndicator(thick=True))
            else:
                coloring = infer_column_coloring(column_values_info, column_values_info.count)
                debug('do_discover_columns', coloring=coloring)
                if coloring == COLORING_NONE or key == metadata.timestamp_field:
                    renderer_main = ColumnRendererColoredPlain()
                    renderer_main.color = '#' + "%02X%02X%02X" % hash_to_rgb(hash_code(column_presentation.title),
                                                                              offset=160)
                    # column_presentation.add_renderer(renderer_main)

                    renderer_indicator = ColumnRendererIndicator()
                    renderer_indicator.color = '#' + "%02X%02X%02X" % hash_to_rgb(hash_code(column_presentation.title),
                                                                                  offset=64)
                    # column_presentation.add_renderer(renderer_indicator)

                    sparse = column_values_info.count is not None and column_values_info.count < POPULATED_RATIO * row_count
                    debug('do_discover_columns', key=key, sparse=sparse, count=column_values_info.count, rows=row_count)

                    if column_values_info.contains_single_value() or sparse:
                        column_presentation.add_renderer(renderer_indicator)
                        column_presentation.add_renderer(renderer_main)
                    else:
                        column_presentation.add_renderer(renderer_main)
                        column_presentation.add_renderer(renderer_indicator)
                else:
                    renderer_main = ColumnRendererColoredHash()
                    if coloring == COLORING_HASH_FREQUENT:
                        renderer_main.onlyFrequent = True
                        renderer_main.color = '#' + "%02X%02X%02X" % hash_to_rgb(hash_code(column_presentation.title), offset=160)
                    else:
                        renderer_main.color = coloring

                    renderer_indicator = ColumnRendererIndicator()
                    renderer_indicator.color = '#' + "%02X%02X%02X" % hash_to_rgb(hash_code(column_presentation.title), offset=64)

                    sparse = column_values_info.count is not None and column_values_info.count < POPULATED_RATIO * row_count
                    debug('do_discover_columns', key=key, sparse=sparse, count=column_values_info.count, rows=row_count)

                    if column_values_info.contains_single_value() or sparse:
                        column_presentation.add_renderer(renderer_indicator)
                        column_presentation.add_renderer(renderer_main)
                    else:
                        column_presentation.add_renderer(renderer_main)
                        column_presentation.add_renderer(renderer_indicator)

                renderer_main.use_single_dict_key = column_metadata.has_one_dict_key


def enhance_column_presentation_renderers(data, values_info: ColumnsValuesInfo, metadata: Metadata, presentation):
    debug('enhance_column_presentation_renderers')
    for record in data:
        for key, value in record.items():
            column_presentation = presentation.columns.get(key)
            debug('enhance_column_presentation_renderers', column_presentation=column_presentation)
            if column_presentation is None or column_presentation.separator:
                continue

            for column_renderer in column_presentation.renderers:
                column_metadata = metadata.columns[key]

                # max_length might be set, but since we got here already, let's refresh it
                if type(column_renderer) is ColumnRendererStripesTimeSeries:
                    sub_presentation = column_presentation.contents
                    if sub_presentation is None:
                        debug('enhance_column_presentation_renderers', values_info_columns=list(values_info.columns))
                        column_presentation.contents = enrich_presentation(
                            value,
                            values_info,
                            column_metadata.metadata,
                            Presentation()
                        )
                else:
                    if type(column_renderer) is ColumnRendererColoredPlain or \
                            type(column_renderer) is ColumnRendererColoredHash or \
                            type(column_renderer) is ColumnRendererColoredMapping:

                        # simulate rendering logic, does not look good
                        if value is None:
                            value_as_string = ''
                        elif column_metadata.has_one_dict_key:
                            value_as_string = single_key_of_dict(value)
                        else:
                            value_as_string = str(value)

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
    threshold = 2.5 * sqrt(records_count)
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
