from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Set, Any

STEREOTYPE_UNKNOWN = 'unknown'  # => None?
STEREOTYPE_TIME_SERIES = 'time_series'


@dataclass
class ColumnMetadata:
    count: int = None
    dictionary: Dict[str, int] = field(default_factory=dict)
    unique_values: Set[str] = field(default_factory=set)
    non_unique_value_counts: Dict[str, int] = field(default_factory=dict)
    complex: bool = None
    type: str = None
    multiline: bool = None
    stereotype: str = None
    min_value: Any = None
    max_value: Any = None
    time_series_timestamp_field: str = None
    time_series_timestamp_format: str = None
    metadata: 'Metadata' = None

    def contains_single_value(self):
        return len(self.non_unique_value_counts) == 1


@dataclass
class Metadata:
    columns: Dict[str, ColumnMetadata] = field(default_factory=lambda: defaultdict(lambda: ColumnMetadata()))
    timestamp_field: str = None
    timestamp_format: str = None
