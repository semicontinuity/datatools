from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Any

STEREOTYPE_UNKNOWN = 'unknown'  # => None?
STEREOTYPE_TIME_SERIES = 'time_series'


@dataclass
class ColumnMetadata:
    count: int = None
    complex: bool = None
    type: str = None
    multiline: bool = None
    has_one_dict_key: bool = None
    stereotype: str = None
    min_value: Any = None
    max_value: Any = None
    time_series_timestamp_field: str = None
    time_series_timestamp_format: str = None
    metadata: 'Metadata' = None


@dataclass
class Metadata:
    columns: Dict[str, ColumnMetadata] = field(default_factory=lambda: defaultdict(lambda: ColumnMetadata()))
    timestamp_field: str = None
    timestamp_format: str = None
