from collections import defaultdict
from dataclasses import dataclass
from math import sqrt
from typing import Dict, Set, Callable, Any, Hashable

from datatools.json.util import is_primitive

COLORING_NONE = "none"
COLORING_SINGLE = "single"
COLORING_HASH_ALL = "hash-all"
COLORING_HASH_FREQUENT = "hash-frequent"


@dataclass
class ColumnAttrs:
    unique_values: Set[str]
    non_unique_value_counts: Dict[str, int]
    value_hashes: Dict[str, int]
    coloring: str = COLORING_NONE

    def get_coloring(self):
        return self.coloring

    def is_colored(self, s: str):
        return self.coloring == COLORING_SINGLE or self.coloring == COLORING_HASH_ALL or (
                self.coloring == COLORING_HASH_FREQUENT and self.is_frequent(s))

    def is_frequent(self, s: str):
        return s in self.non_unique_value_counts


def compute_column_attrs(j, column_id: Hashable, cell_value_function: Callable[[Any, Any], Any]) -> ColumnAttrs:
    attr = ColumnAttrs(set(), defaultdict(int), {})
    for record in j:
        cell = cell_value_function(record, column_id)
        if cell is ... or cell is None or not is_primitive(cell):
            continue
        value_as_string = str(cell)

        count = attr.non_unique_value_counts.get(value_as_string)
        if count is None:
            if value_as_string in attr.unique_values:
                attr.unique_values.remove(value_as_string)
                attr.non_unique_value_counts[value_as_string] = 2
            else:
                attr.unique_values.add(value_as_string)
        else:
            attr.non_unique_value_counts[value_as_string] = count + 1
    attr.coloring = compute_column_coloring(attr, len(j))
    return attr


def compute_column_coloring(column_attr: ColumnAttrs, row_count: int):
    threshold = 2.5 * sqrt(row_count)
    if len(column_attr.non_unique_value_counts) == 1 and len(column_attr.unique_values) == 0:
        return COLORING_SINGLE
    elif len(column_attr.non_unique_value_counts) == 0 or (len(column_attr.unique_values) == 0 and len(column_attr.non_unique_value_counts) == 1):
        return COLORING_NONE
    elif len(column_attr.unique_values) + len(column_attr.non_unique_value_counts) < threshold:
        return COLORING_HASH_ALL
    elif 0 < len(column_attr.non_unique_value_counts) < threshold:
        return COLORING_HASH_FREQUENT
    else:
        return COLORING_NONE
