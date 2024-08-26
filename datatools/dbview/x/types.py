from dataclasses import dataclass
from typing import List, Optional


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


@dataclass
class DbReferrers(EntityReference):
    table: str
    selector: List[DbSelectorClause]


@dataclass
class View:
    def run(self) -> Optional[EntityReference]:
        pass
