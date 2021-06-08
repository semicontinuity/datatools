from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Set

from datatools.json.coloring import COLORING_NONE
from datatools.json.util import is_primitive

column_is_complex = defaultdict(bool)
max_column_widths: Dict[str, int] = defaultdict(int)


@dataclass
class ColumnAttrs:
    unique_values: Set[str]
    non_unique_value_counts: Dict[str, int]

    value_stats: Dict[str, int]
    non_uniques_count: int = 0
    coloring: str = COLORING_NONE

    def contains_single_value(self):
        return len(self.non_unique_value_counts) == 1


column_attrs_map = defaultdict(lambda: ColumnAttrs(set(), {}, defaultdict(int)))


def infer_metadata(data, cell_is_stripes):
    for record in data:
        for key, value in record.items():
            value_as_string = ' ' if value is None else str(value)  # quick an dirty

            if type(value) is dict or type(value) is list or "\n" in value_as_string:
                column_is_complex[key] = True
            else:
                column_attr = column_attrs_map[key]
                column_attr.value_stats[value_as_string] = column_attr.value_stats.get(value_as_string, 0) + 1

            cell_length = len(value) if cell_is_stripes(key) else (
                0 if "\n" in value_as_string else len(value_as_string))
            max_column_widths[key] = max(max_column_widths[key], cell_length)


def compute_stats(data):
    for record in data:
        for key, value in record.items():
            if key in column_is_complex:
                continue

            attr = column_attrs_map[key]
            if value is ... or value is None or not is_primitive(value):
                continue
            value_as_string = str(value)

            count = attr.non_unique_value_counts.get(value_as_string)
            if count is None:
                if value_as_string in attr.unique_values:
                    attr.unique_values.remove(value_as_string)
                    attr.non_unique_value_counts[value_as_string] = 2
                else:
                    attr.unique_values.add(value_as_string)
            else:
                attr.non_unique_value_counts[value_as_string] = count + 1