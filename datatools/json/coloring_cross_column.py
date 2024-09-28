from collections import defaultdict
from typing import Dict, List, Callable, Any

from datatools.json.coloring import COLORING_NONE, COLORING_SINGLE
from datatools.json.util import is_primitive


def compute_cross_column_attrs(j, column_attrs_by_name, cell_value_function: Callable[[Any, Any], Any]):
    indices2categories = defaultdict(list)

    for column_id, attr in column_attrs_by_name.items():
        if attr.coloring == COLORING_NONE or attr.coloring == COLORING_SINGLE:
            continue

        value2indices: Dict[str, List[int]] = defaultdict(list)
        for r, record in enumerate(j):
            cell = cell_value_function(record, column_id)
            if cell is None or not is_primitive(cell):
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
