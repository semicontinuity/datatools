from dataclasses import dataclass
from typing import Any, Callable

from datatools.jt.model.column_state import ColumnState
from datatools.jt.model.metadata import ColumnMetadata
from datatools.jt.model.values_info import ValuesInfo


@dataclass
class RenderData:
    column_values_info: ValuesInfo
    column_metadata: ColumnMetadata
    column_presentation: 'ColumnPresentation'
    column_state: ColumnState
    column_key: str
    size: int
    named_cell_value_f: Callable[[int, str], Any]
    value: Callable[[int], Any] # does not work?
