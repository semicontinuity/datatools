from collections import defaultdict
from dataclasses import dataclass
from math import sqrt
from typing import Dict, Any

from datatools.json.util import dataclass_from_dict
from datatools.jt.auto_metadata import ColumnMetadata


COLORING_NONE = "none"
COLORING_HASH_ALL = "hash-all"
COLORING_HASH_FREQUENT = "hash-frequent"
COLORING_HASH_ASSISTANT_COLUMN = "hash-assistant-column"


@dataclass
class ColumnPresentation:
    title: str = None
    coloring: str = COLORING_NONE
    separator: bool = None
    indicator: bool = None
    stripes: bool = None
    max_length: int = 0
    collapsed: bool = None
    assistant_column: str = None


def infer_presentation(data, column_metadata_map: Dict[str, ColumnMetadata], raw_presentation: Dict[str, Any]):
    raw_columns_presentation = raw_presentation.get("columns")
    if raw_columns_presentation:
        return {k: dataclass_from_dict(ColumnPresentation, v) for k, v in raw_columns_presentation.items()}

    column_presentation_map = defaultdict(lambda: ColumnPresentation())

    for key, column_metadata in column_metadata_map.items():
        column_presentation = column_presentation_map[key]
        column_presentation.title = key

        # assume that all lists are stripes for now
        if column_metadata.type == 'list' and (column_metadata.stereotype == 'hashes' or column_metadata.stereotype == 'time_series'):
            column_presentation.stripes = True
        elif column_metadata.complex or column_metadata.multiline:
            column_presentation.indicator = True
        else:
            column_presentation.coloring = infer_column_coloring(column_metadata, len(data))
            column_presentation.collapsed = column_metadata.contains_single_value()

    for record in data:
        for key, value in record.items():
            column_presentation = column_presentation_map[key]
            if column_presentation.indicator:
                continue
            elif column_presentation.stripes:
                column_presentation.max_length = max(column_presentation.max_length, len(value))
            else:
                value_as_string = '' if value is None else str(value)  # quick and dirty
                column_presentation.max_length = max(column_presentation.max_length, len(value_as_string))

    return column_presentation_map


def infer_column_coloring(column_metadata, records_count) -> str:
    threshold = 2 * sqrt(records_count)
    if len(column_metadata.unique_values) + len(column_metadata.non_unique_value_counts) < threshold:
        return COLORING_HASH_ALL
    elif len(column_metadata.non_unique_value_counts) < threshold:
        return COLORING_HASH_FREQUENT
    else:
        return COLORING_NONE
