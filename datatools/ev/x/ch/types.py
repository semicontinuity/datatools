from dataclasses import dataclass

from datatools.dbview.x.util.db_query import DbQuery
from datatools.ev.app_types import EntityReference
from datatools.ev.x.pg.types import DbTableRowsSelector


@dataclass(kw_only=True)
class ClickhouseRowEntity(EntityReference):
    selector: DbTableRowsSelector
    query: DbQuery = None


@dataclass(kw_only=True)
class ClickhouseRowsEntity(EntityReference):
    selector: DbTableRowsSelector
    query: DbQuery = None
