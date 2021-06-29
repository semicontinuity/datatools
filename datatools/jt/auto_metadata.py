from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Set

from datatools.json.util import is_primitive
from datatools.util.time_series_util import time_series_list_summary
from datatools.util.time_util import infer_timestamp_format


@dataclass
class ColumnMetadata:
    unique_values: Set[str] = field(default_factory=set)
    non_unique_value_counts: Dict[str, int] = field(default_factory=dict)
    complex: bool = None
    type: str = None
    multiline: bool = None
    stereotype: str = None
    time_series_timestamp_field: str = None
    time_series_timestamp_format: str = None
    time_series_timestamp_min: float = None
    time_series_timestamp_max: float = None
    metadata: 'Metadata' = None

    def contains_single_value(self):
        return len(self.non_unique_value_counts) == 1


@dataclass
class Metadata:
    columns: Dict[str, ColumnMetadata] = field(default_factory=lambda: defaultdict(lambda: ColumnMetadata(set(), {})))
    timestamp_field: str = None
    timestamp_format: str = None


def infer_metadata(data, metadata: Metadata):
    raw_columns_metadata = metadata.columns
    if raw_columns_metadata:
        return metadata, raw_columns_metadata

    timestamp_formats = infer_metadata0(data, metadata.columns)
    good_timestamp_formats = [(k, v) for k, v in timestamp_formats.items() if v != '']
    if len(good_timestamp_formats) == 1:
        metadata.timestamp_field = good_timestamp_formats[0][0]
        metadata.timestamp_format = good_timestamp_formats[0][1]

    infer_metadata1(data, metadata.columns)
    return metadata, metadata.columns


def infer_metadata0(data, column_metadata_map: Dict[str, ColumnMetadata]):
    timestamp_formats = {}
    for record in data:
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
                if column_metadata.stereotype is None or column_metadata.stereotype == 'time_series':
                    descriptor = time_series_list_summary(value)
                    if descriptor is not None:
                        update_time_series_metadata(column_metadata, descriptor)
                        continue
                column_metadata.stereotype = 'unknown'
            else:
                column_metadata.type = 'primitive'
                if type(value) is str:
                    current_ts_format = timestamp_formats.get(key)
                    if '\n' in value:
                        column_metadata.multiline = True
                        timestamp_formats[key] = ''
                    elif current_ts_format != '':
                        format, _ = infer_timestamp_format(value)
                        if format != current_ts_format:
                            timestamp_formats[key] = format if current_ts_format is None else ''
    return timestamp_formats


def update_time_series_metadata(column_metadata: ColumnMetadata, descriptor):
    if column_metadata.stereotype is None:
        column_metadata.stereotype = 'time_series'
        column_metadata.time_series_timestamp_field = descriptor[0]
        column_metadata.time_series_timestamp_format = descriptor[1]
        column_metadata.time_series_timestamp_min = descriptor[2]
        column_metadata.time_series_timestamp_max = descriptor[3]
        return

    if column_metadata.stereotype == 'time_series'\
            and column_metadata.time_series_timestamp_field == descriptor[0]\
            and column_metadata.time_series_timestamp_format == descriptor[1]:
        column_metadata.time_series_timestamp_min = min(descriptor[2], column_metadata.time_series_timestamp_min)
        column_metadata.time_series_timestamp_max = max(descriptor[3], column_metadata.time_series_timestamp_max)
        return

    column_metadata.stereotype = 'unknown'
    column_metadata.time_series_timestamp_format = None
    column_metadata.time_series_timestamp_min = None
    column_metadata.time_series_timestamp_max = None


def infer_metadata1(data, column_metadata_map):
    for record in data:
        for key, value in record.items():
            column_metadata = column_metadata_map[key]
            if column_metadata.complex or column_metadata.complex:
                continue

            if value is ... or value is None or not is_primitive(value):
                continue
            value_as_string = str(value)

            count = column_metadata.non_unique_value_counts.get(value_as_string)
            if count is None:
                if value_as_string in column_metadata.unique_values:
                    column_metadata.unique_values.remove(value_as_string)
                    column_metadata.non_unique_value_counts[value_as_string] = 2
                else:
                    column_metadata.unique_values.add(value_as_string)
            else:
                column_metadata.non_unique_value_counts[value_as_string] = count + 1
