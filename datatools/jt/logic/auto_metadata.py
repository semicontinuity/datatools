from typing import Dict

from datatools.jt.logic.auto_values_info import compute_values_info
from datatools.jt.model.metadata import ColumnMetadata, STEREOTYPE_UNKNOWN, STEREOTYPE_TIME_SERIES, Metadata
from datatools.util.logging import debug
from datatools.util.time_series_util import time_series_list_summary
from datatools.util.time_util import infer_timestamp_format


def enrich_metadata(data, metadata: Metadata) -> Metadata:
    infer_metadata_time_fields(data, metadata)
    debug('enrich_metadata', metadata_columns=metadata.columns.keys())
    compute_values_info(data, metadata.columns)
    return metadata


def infer_metadata_time_fields(data, metadata):
    debug('infer_metadata_time_fields', metadata_columns_keys=metadata.columns.keys())
    timestamp_formats = infer_metadata0(data, metadata.columns)
    good_timestamp_formats = [(k, v) for k, v in timestamp_formats.items() if v != '']
    if len(good_timestamp_formats) == 1:
        metadata.timestamp_field = good_timestamp_formats[0][0]
        metadata.timestamp_format = good_timestamp_formats[0][1]


def infer_metadata0(data, column_metadata_map: Dict[str, ColumnMetadata]):
    timestamp_formats = {}
    for record in data:
        if type(record) != dict:
            continue    # ersatz
        for key, value in record.items():
            column_metadata = column_metadata_map[key]
            if type(value) is dict:
                column_metadata.complex = True
                if column_metadata.type is None:
                    column_metadata.type = 'dict'
                elif column_metadata.type != 'dict':
                    column_metadata.type = 'any'
            elif type(value) is list:
                column_metadata.complex = True
                if column_metadata.type is None:
                    column_metadata.type = 'list'
                elif column_metadata.type != 'list':
                    column_metadata.type = 'any'

                # replace with 'reducer'
                if column_metadata.stereotype is None or column_metadata.stereotype == STEREOTYPE_TIME_SERIES:
                    if column_metadata.metadata is None:    # Ersatz
                        column_metadata.metadata = Metadata()
                        infer_metadata_time_fields(value, column_metadata.metadata)

                    descriptor = time_series_list_summary(value)
                    if descriptor is not None:
                        if not update_time_series_metadata(column_metadata, descriptor):
                            debug('infer_metadata0', value=value)
                        continue

                debug('infer_metadata0', key=key, stereotype=STEREOTYPE_UNKNOWN)
                column_metadata.stereotype = STEREOTYPE_UNKNOWN
            else:
                column_metadata.type = 'primitive'
                if type(value) is str:
                    current_ts_format = timestamp_formats.get(key)
                    if '\n' in value:
                        column_metadata.multiline = True
                        timestamp_formats[key] = ''
                    elif current_ts_format != '':
                        fmt, _ = infer_timestamp_format(value)
                        if fmt != current_ts_format:
                            timestamp_formats[key] = fmt if current_ts_format is None else ''
    return timestamp_formats


def update_time_series_metadata(column_metadata: ColumnMetadata, descriptor) -> bool:
    if column_metadata.stereotype is None:
        # First occurrence
        column_metadata.stereotype = STEREOTYPE_TIME_SERIES
        column_metadata.time_series_timestamp_field = descriptor[0]
        column_metadata.time_series_timestamp_format = descriptor[1]
        column_metadata.min_value = descriptor[2]
        column_metadata.max_value = descriptor[3]
        return True

    if column_metadata.stereotype == STEREOTYPE_TIME_SERIES:
        # Subsequent occurrences:
        if descriptor[0] == column_metadata.time_series_timestamp_field and descriptor[1] == column_metadata.time_series_timestamp_format:
            column_metadata.min_value = accumulate(min, column_metadata.min_value, descriptor[2])
            column_metadata.max_value = accumulate(max, column_metadata.max_value, descriptor[3])
            return True
        else:
            debug(
                'infer_metadata0',
                timestamp_field=descriptor[0],
                prev_timestamp_field=column_metadata.time_series_timestamp_field,
                timestamp_format=descriptor[1],
                prev_timestamp_format=column_metadata.time_series_timestamp_format,
            )

    column_metadata.stereotype = STEREOTYPE_UNKNOWN
    column_metadata.time_series_timestamp_format = None
    column_metadata.min_value = None
    column_metadata.max_value = None
    return False


def accumulate(func, acc, value):
    return func(value, acc) if acc is not None else value
