from dataclasses import dataclass
from math import sqrt
from typing import Dict, Set, List, Callable, Any, Hashable
from collections import defaultdict


def hash_code(s):
    """ Consistent hash """
    hh = 0
    for c in s:
        hh = (31 * hh + ord(c)) % 4294967296
    return hh


def hash_to_rgb(h):
    if h is None:
        return 0, 0, 0

    r6 = (h % 2) & 1
    h = (h - r6) // 2
    g6 = (h % 2) & 1
    h = (h - g6) // 2
    b6 = (h % 2) & 1
    h = (h - b6) // 2

    r5 = (h % 2) & 1
    h = (h - r5) // 2
    g5 = (h % 2) & 1
    h = (h - g5) // 2
    b5 = (h % 2) & 1
    h = (h - b5) // 2

    r3 = (h % 3) & 0x3
    h = (h - r3) // 4
    g3 = (h % 3) & 0x3
    h = (h - g3) // 4
    b3 = (h % 3) & 0x3

    return r6*16 + r5*8 + r3 + 0xE0, g6*16 + g5*8 + g3 + 0xE0, b6*16 + b5*8 + b3 + 0xE0


def hash_to_rgb_dark(h):
    if h is None:
        return 0, 0, 0

    r6 = h % 2
    h = (h - r6) // 2
    g6 = h % 2
    h = (h - g6) // 2
    b6 = h % 2
    h = (h - g6) // 2

    r3 = h % 32
    h = (h - r3) // 32
    g3 = h % 32
    h = (h - g3) // 32
    b3 = h % 32

    return r6 * 32 + r3, g6 * 32 + g3, b6 * 32 + b3


def is_primitive_type(value):
    return type(value).__name__ in {'NoneType', 'int', 'float', 'str', 'bool'}


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
                self.coloring == COLORING_HASH_FREQUENT and s in self.non_unique_value_counts)


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


def compute_column_attrs(j, column_id: Hashable, cell_value_function: Callable[[Any, Any], Any]) -> ColumnAttrs:
    attr = ColumnAttrs(set(), defaultdict(int), {})
    for record in j:
        cell = cell_value_function(record, column_id)
        if cell is ... or cell is None or not is_primitive_type(cell):
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


def compute_cross_column_attrs(j, column_attrs_by_name, cell_value_function: Callable[[Any, Any], Any]):
    indices2categories = defaultdict(list)

    for column_id, attr in column_attrs_by_name.items():
        if attr.coloring == COLORING_NONE or attr.coloring == COLORING_SINGLE:
            continue

        value2indices: Dict[str, List[int]] = defaultdict(list)
        for r, record in enumerate(j):
            cell = cell_value_function(record, column_id)
            if cell is None or not is_primitive_type(cell):
                continue
            value_as_string = str(cell)
            if attr.is_colored(value_as_string):
                value2indices[value_as_string].append(r)
        for value, indices in value2indices.items():
            indices2categories[tuple(indices)].append((column_id, value))

    for indices, categories in indices2categories.items():
        if len(categories) > 1:
            for column_id, value in categories:
                column_attrs_by_name[column_id].value_hashes[value] = hash(indices)
