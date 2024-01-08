from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class ValuesStats:
    count: int = None
    dictionary: Dict[str, int] = field(default_factory=dict)
    unique_values: Set[str] = field(default_factory=set)
    non_unique_value_counts: Dict[str, int] = field(default_factory=dict)

    def contains_single_value(self):
        return self.count is not None and self.count > 1 and ((len(self.non_unique_value_counts) == 1 and len(self.unique_values) == 0) or (len(self.non_unique_value_counts) == 0 and len(self.unique_values) == 1))


@dataclass
class ColumnsValuesStats:
    columns: Dict[str, ValuesStats] = field(default_factory=lambda: defaultdict(lambda: ValuesStats()))
