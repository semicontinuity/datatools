from math import sqrt
from typing import List

from datatools.jt.auto_metadata import column_attrs_map, max_column_widths, column_is_complex

COLORING_NONE = "none"
COLORING_HASH_ALL = "hash-all"
COLORING_HASH_FREQUENT = "hash-frequent"


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


def infer_presentation(data):
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
