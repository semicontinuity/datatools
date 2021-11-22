from typing import Dict

from datatools.json.util import is_primitive
from datatools.jt.model.metadata import ColumnMetadata, STEREOTYPE_UNKNOWN, STEREOTYPE_TIME_SERIES, Metadata
from datatools.util.time_series_util import time_series_list_summary
from datatools.util.time_util import infer_timestamp_format


def enrich_metadata(data, metadata: Metadata) -> Metadata:
    # if metadata.columns:
    #     return metadata

    timestamp_formats = infer_metadata0(data, metadata.columns)
    good_timestamp_formats = [(k, v) for k, v in timestamp_formats.items() if v != '']
    if len(good_timestamp_formats) == 1:
        metadata.timestamp_field = good_timestamp_formats[0][0]
        metadata.timestamp_format = good_timestamp_formats[0][1]

    infer_metadata1(data, metadata.columns)
    return metadata


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
                        infer_metadata0(value, column_metadata.metadata.columns)

                    descriptor = time_series_list_summary(value)
                    if descriptor is not None:
                        update_time_series_metadata(column_metadata, descriptor)
                        continue
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


def update_time_series_metadata(column_metadata: ColumnMetadata, descriptor):
    if column_metadata.stereotype is None:
        column_metadata.stereotype = STEREOTYPE_TIME_SERIES
        column_metadata.time_series_timestamp_field = descriptor[0]
        column_metadata.time_series_timestamp_format = descriptor[1]
        column_metadata.min_value = descriptor[2]
        column_metadata.max_value = descriptor[3]
        return

    if column_metadata.stereotype == STEREOTYPE_TIME_SERIES \
            and column_metadata.time_series_timestamp_field == descriptor[0]\
            and column_metadata.time_series_timestamp_format == descriptor[1]:
        column_metadata.min_value = accumulate(min, column_metadata.min_value, descriptor[2])
        column_metadata.max_value = accumulate(max, column_metadata.max_value, descriptor[3])
        return

    column_metadata.stereotype = STEREOTYPE_UNKNOWN
    column_metadata.time_series_timestamp_format = None
    column_metadata.min_value = None
    column_metadata.max_value = None


def infer_metadata1(data, column_metadata_map):
    for record in data:
        for key, value in record.items():
            column_metadata = column_metadata_map[key]
            if column_metadata.count is None:
                column_metadata.count = 0
            column_metadata.count += 1
            if column_metadata.complex or column_metadata.complex:
                continue

            if value is ... or value is None or not is_primitive(value):
                continue
            value_as_string = str(value)

            dict_index = column_metadata.dictionary.get(value_as_string)
            if dict_index is None:
                dict_index = len(column_metadata.dictionary)
            column_metadata.dictionary[value_as_string] = dict_index

            non_unique_value_count = column_metadata.non_unique_value_counts.get(value_as_string)
            if non_unique_value_count is None:
                if value_as_string in column_metadata.unique_values:
                    column_metadata.unique_values.remove(value_as_string)
                    column_metadata.non_unique_value_counts[value_as_string] = 2
                else:
                    column_metadata.unique_values.add(value_as_string)
            else:
                column_metadata.non_unique_value_counts[value_as_string] = non_unique_value_count + 1


def accumulate(func, acc, value):
    return func(value, acc) if acc is not None else value
