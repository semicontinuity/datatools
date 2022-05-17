from dataclasses import dataclass
from typing import Any, Callable

from datatools.jt.model.column_state import ColumnState
from datatools.jt.model.metadata import ColumnMetadata


@dataclass
class RenderData:
    column_metadata: ColumnMetadata
    column_presentation: 'ColumnPresentation'
    column_state: ColumnState
    column_key: str
    size: int
    named_cell_value_f: Callable[[int, str], Any]
