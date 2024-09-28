from collections import defaultdict
from math import sqrt
from typing import Dict, Set, Callable, Any, Hashable

from datatools.json.util import is_primitive

COLORING_NONE = "none"
COLORING_SINGLE = "single"
COLORING_HASH_ALL = "hash-all"
COLORING_HASH_FREQUENT = "hash-frequent"


class ColumnAttrs:
    value_count: int
    unique_values: Set[str]
    non_unique_value_counts: Dict[str, int]
    value_hashes: Dict[str, int]
    coloring: str = COLORING_NONE

    def __init__(self):
        self.value_count = 0
        self.unique_values = set()
        self.non_unique_value_counts = defaultdict(int)
        self.value_hashes = {}

    def add_value(self, value: str):
        if value is ... or value is None or not is_primitive(value):
            return

        self.value_count += 1
        count = self.non_unique_value_counts.get(value)
        if count is None:
            if value in self.unique_values:
                self.unique_values.remove(value)
                self.non_unique_value_counts[value] = 2
            else:
                self.unique_values.add(value)
        else:
            self.non_unique_value_counts[value] = count + 1

    def compute_coloring(self):
        self.coloring = self._do_compute_coloring()

    def _do_compute_coloring(self):
        threshold = 2.5 * sqrt(self.value_count)
        if len(self.non_unique_value_counts) == 1 and len(self.unique_values) == 0:
            return COLORING_SINGLE
        elif len(self.non_unique_value_counts) == 0:
            return COLORING_NONE
        elif len(self.unique_values) == 0 and len(self.non_unique_value_counts) == 1:
            return COLORING_NONE
        elif len(self.unique_values) + len(self.non_unique_value_counts) < threshold:
            return COLORING_HASH_ALL
        elif 0 < len(self.non_unique_value_counts) < threshold:
            return COLORING_HASH_FREQUENT
        else:
            return COLORING_NONE

    def get_coloring(self):
        return self.coloring

    def is_colored(self, s: str):
        return self.coloring == COLORING_SINGLE or self.coloring == COLORING_HASH_ALL or (
                self.coloring == COLORING_HASH_FREQUENT and self.is_frequent(s))

    def is_frequent(self, s: str):
        return s in self.non_unique_value_counts
