from dataclasses import dataclass
from typing import Any

from datatools.dbview.x.util.db_query import DbQuery


@dataclass
class DbEntityData:
    query: DbQuery
    rows: list[dict[str, Any]]
    pks: list[str]
    references: dict[str, Any]
    realm_ctx: str = None