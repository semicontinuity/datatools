from collections import defaultdict
from dataclasses import dataclass
from math import sqrt
from typing import Dict, List

COLORING_NONE = "none"
COLORING_HASH_ALL = "hash-all"
COLORING_HASH_FREQUENT = "hash-frequent"


@dataclass
class ColumnAttrs:
    value_stats: Dict[str, int]
    non_uniques_count: int = 0
    coloring: str = COLORING_NONE


column_attrs_map = defaultdict(lambda: ColumnAttrs(defaultdict(int)))
column_is_complex = defaultdict(bool)
max_column_widths: Dict[str, int] = defaultdict(int)


# TODO: if some column is not present for some rows, it should be included with smaller priority (after other columns)
def pick_displayed_columns(screen_width) -> List[str]:
    """ Pick columns until they fit screen """
    result = []
    screen_width -= 1

    # simple columns first
    for k, v in max_column_widths.items():
        if 0 < v <= screen_width - 1 and not column_is_complex[k]:
            result.append(k)
            screen_width -= (v + 1)

    # complex columns second
    for k, v in max_column_widths.items():
        if 0 < v <= screen_width - 1 and column_is_complex[k]:
            result.append(k)
            screen_width -= (v + 1)

    return result


def analyze_data(data, cell_is_stripes):
    for record in data:
        for key, value in record.items():
            value_as_string = ' ' if value is None else str(value)   # quick an dirty

            if type(value) is dict or type(value) is list:
                column_is_complex[key] = True
            else:
                column_attr = column_attrs_map[key]
                column_attr.value_stats[value_as_string] = column_attr.value_stats.get(value_as_string, 0) + 1

            cell_length = len(value) if cell_is_stripes(key) else len(value_as_string)
            max_column_widths[key] = max(max_column_widths[key], cell_length)

    for key, column_attr in column_attrs_map.items():
        for word, count in column_attr.value_stats.items():
            if count > 1:
                column_attr.non_uniques_count += 1

    for column_attrs in column_attrs_map.values():
        column_attrs.coloring = compute_column_coloring(column_attrs, len(data))


def compute_column_coloring(column_attrs, records_count) -> str:
    threshold = 2 * sqrt(records_count)
    nu = column_attrs.non_uniques_count
    if len(column_attrs.value_stats) < threshold:
        return COLORING_HASH_ALL
    elif nu < threshold:
        return COLORING_HASH_FREQUENT
    else:
        return COLORING_NONE
