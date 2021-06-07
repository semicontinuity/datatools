from collections import defaultdict
from dataclasses import dataclass
from typing import Dict

from datatools.json.coloring import COLORING_NONE

column_is_complex = defaultdict(bool)
max_column_widths: Dict[str, int] = defaultdict(int)


@dataclass
class ColumnAttrs:
    value_stats: Dict[str, int]
    non_uniques_count: int = 0
    coloring: str = COLORING_NONE


column_attrs_map = defaultdict(lambda: ColumnAttrs(defaultdict(int)))


def infer_metadata(data, cell_is_stripes):
    for record in data:
        for key, value in record.items():
            value_as_string = ' ' if value is None else str(value)  # quick an dirty

            if type(value) is dict or type(value) is list:
                column_is_complex[key] = True
            else:
                column_attr = column_attrs_map[key]
                column_attr.value_stats[value_as_string] = column_attr.value_stats.get(value_as_string, 0) + 1

            if "\n" in value_as_string: continue

            cell_length = len(value) if cell_is_stripes(key) else (
                0 if "\n" in value_as_string else len(value_as_string))
            max_column_widths[key] = max(max_column_widths[key], cell_length)
