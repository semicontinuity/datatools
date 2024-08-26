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
class DbTableRowsSelector:
    table: str
    where: List[DbSelectorClause]


@dataclass
class DbRowReference(EntityReference):
    selector: DbTableRowsSelector


@dataclass
class DbReferrers(EntityReference):
    selector: DbTableRowsSelector


@dataclass
class View:
    def run(self) -> Optional[EntityReference]:
        pass
