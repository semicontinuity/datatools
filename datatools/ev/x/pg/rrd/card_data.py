from dataclasses import dataclass
from typing import Any

from datatools.dbview.x.util.result_set_metadata import ResultSetMetadata


@dataclass
class CardData:
    rows: list[dict[str, Any]]
    metadata: ResultSetMetadata
