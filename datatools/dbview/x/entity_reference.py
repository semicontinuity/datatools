from dataclasses import dataclass
from typing import List


@dataclass
class EntityReference:
    pass


@dataclass
class DbSelectorClause:
    column: str
    op: str
    value: str


@dataclass
class DbRowReference(EntityReference):
    table: str
    selector: List[DbSelectorClause]
