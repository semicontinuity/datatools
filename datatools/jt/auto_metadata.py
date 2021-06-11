from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Set

from datatools.json.util import is_primitive, dataclass_from_dict
from datatools.util.text_util import infer_timestamp_format


@dataclass
class ColumnMetadata:
    unique_values: Set[str]
    non_unique_value_counts: Dict[str, int]
    complex: bool = None
    type: str = None
    multiline: bool = None

    def contains_single_value(self):
        return len(self.non_unique_value_counts) == 1


def infer_metadata(data, raw_metadata):
    raw_columns_metadata = raw_metadata.get("columns")
    if raw_columns_metadata:
        return {k: dataclass_from_dict(ColumnMetadata, v) for k, v in raw_columns_metadata.items()}

    column_metadata_map = defaultdict(lambda: ColumnMetadata(set(), {}))
    timestamp_formats = infer_metadata0(data, column_metadata_map)
    good_timestamp_formats = [(k, v) for k, v in timestamp_formats.items() if v != '']
    if len(good_timestamp_formats) == 1:
        raw_metadata['timestamp_field'] = good_timestamp_formats[0][0]
        raw_metadata['timestamp_format'] = good_timestamp_formats[0][1]
    infer_metadata1(data, column_metadata_map)
    return column_metadata_map


def infer_metadata0(data, column_metadata_map):
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
