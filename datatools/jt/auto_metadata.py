from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Set

from datatools.json.util import is_primitive, dataclass_from_dict


@dataclass
class ColumnMetadata:
    unique_values: Set[str]
    non_unique_value_counts: Dict[str, int]
    complex: bool = None

    def contains_single_value(self):
        return len(self.non_unique_value_counts) == 1


def infer_metadata(data, raw_metadata):
    raw_columns_metadata = raw_metadata.get("columns")
    if raw_columns_metadata:
        return {k: dataclass_from_dict(ColumnMetadata, v) for k, v in raw_columns_metadata.items()}

    column_metadata_map = defaultdict(lambda: ColumnMetadata(set(), {}))
    infer_metadata0(data, column_metadata_map)
    infer_metadata1(data, column_metadata_map)
    return column_metadata_map


def infer_metadata0(data, column_metadata_map):
    for record in data:
        for key, value in record.items():
            value_as_string = ' ' if value is None else str(value)  # quick an dirty

            column_metadata = column_metadata_map[key]
            if type(value) is dict or type(value) is list or "\n" in value_as_string:
                column_metadata.complex = True


def infer_metadata1(data, column_metadata_map):
    for record in data:
        for key, value in record.items():
            column_metadata = column_metadata_map[key]
            if column_metadata.complex:
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
