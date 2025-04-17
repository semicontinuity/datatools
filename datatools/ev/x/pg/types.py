from dataclasses import dataclass
from typing import List

from datatools.dbview.x.util.db_query import DbQuery
from datatools.ev.app_types import EntityReference


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
class DbRowsReference(EntityReference):
    selector: DbTableRowsSelector
    query: DbQuery = None


@dataclass(kw_only=True)
class DbRowReference(EntityReference):
    selector: DbTableRowsSelector
    query: DbQuery = None


@dataclass(kw_only=True)
class DbReferrers(EntityReference):
    selector: DbTableRowsSelector
    query: DbQuery = None


@dataclass(kw_only=True)
class DbReferringTables(EntityReference):
    selector: DbTableRowsSelector
    query: DbQuery = None
