from dataclasses import dataclass
from typing import Any


@dataclass
class DbEntityData:
    rows: list[dict[str, Any]]
    pks: list[str]
    references: dict[str, Any]
