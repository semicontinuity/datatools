from collections import defaultdict
from dataclasses import dataclass
from math import sqrt
from typing import List, Dict, Any

from datatools.json.util import dataclass_from_dict
from datatools.jt.auto_metadata import ColumnMetadata

max_column_widths: Dict[str, int] = defaultdict(int)

COLORING_NONE = "none"
COLORING_HASH_ALL = "hash-all"
COLORING_HASH_FREQUENT = "hash-frequent"


@dataclass
class ColumnPresentation:
    coloring: str = COLORING_NONE
    stripes: bool = None


# TODO: if some column is not present for some rows, it should be included with smaller priority (after other columns)
def pick_displayed_columns(screen_width, column_metadata_map, column_presentation_map) -> List[str]:
    """ Pick columns until they fit screen """
    result = []
    screen_width -= 1

    # simple columns first
    for k, v in max_column_widths.items():
        if 0 < v <= screen_width - 1 and not column_metadata_map[k].complex:
            result.append(k)
            screen_width -= (v + 1)

    # complex columns second
    for k, v in max_column_widths.items():
        if 0 < v <= screen_width - 1 and column_metadata_map[k].complex:
            result.append(k)
            screen_width -= (v + 1)

    return result


def infer_presentation(data, column_metadata_map: Dict[str, ColumnMetadata], raw_presentation: Dict[str, Any]):
    raw_columns_presentation = raw_presentation.get("columns")
    if raw_columns_presentation:
        return {k: dataclass_from_dict(ColumnPresentation, v) for k, v in raw_columns_presentation.items()}

    column_presentation_map = defaultdict(lambda: ColumnPresentation())
    infer_presentation1(data, column_metadata_map, column_presentation_map)
    infer_presentation2(data, column_presentation_map)
    return column_presentation_map


def infer_presentation1(data, column_metadata_map, column_presentation_map):
    for key, column_metadata in column_metadata_map.items():
        column_presentation_map[key].coloring = compute_column_coloring(column_metadata, len(data))


def infer_presentation2(data, column_presentation_map):
    for record in data:
        for key, value in record.items():
            value_as_string = ' ' if value is None else str(value)  # quick and dirty
            column_presentation = column_presentation_map[key]

            cell_length = len(value) if column_presentation.stripes else (
                0 if "\n" in value_as_string else len(value_as_string))
            max_column_widths[key] = max(max_column_widths[key], cell_length)


def compute_column_coloring(column_metadata, records_count) -> str:
    threshold = 2 * sqrt(records_count)
    if len(column_metadata.unique_values) + len(column_metadata.non_unique_value_counts) < threshold:
        return COLORING_HASH_ALL
    elif len(column_metadata.non_unique_value_counts) < threshold:
        return COLORING_HASH_FREQUENT
    else:
        return COLORING_NONE
