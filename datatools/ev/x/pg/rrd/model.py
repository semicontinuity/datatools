from dataclasses import dataclass
from typing import Any


@dataclass
class CardData:
    table: str
    pks: list[str]
    rows: list[dict[str, Any]]
