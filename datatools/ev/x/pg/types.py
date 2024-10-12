from dataclasses import dataclass
from typing import List, Dict, Any

from datatools.ev.app_types import EntityReference
from datatools.dbview.util.pg import get_table_foreign_keys_outbound


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
class DbTableColumn:
    table: str
    column: str


@dataclass(kw_only=True)
class DbRowReference(EntityReference):
    selector: DbTableRowsSelector


@dataclass(kw_only=True)
class DbReferrers(EntityReference):
    selector: DbTableRowsSelector


@dataclass(kw_only=True)
class DbReferringRows(EntityReference):
    source: DbTableColumn
    target: DbTableRowsSelector
