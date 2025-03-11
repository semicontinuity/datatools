from dataclasses import dataclass
from typing import Any

from datatools.dbview.x.util.db_query import DbQuery
from datatools.dbview.x.util.result_set_metadata import ResultSetMetadata


@dataclass
class DbEntityData:
    query: DbQuery
    rows: list[dict[str, Any]]
    pks: list[str]
    references: dict[str, Any]
    realm_ctx: str = None
    realm_ctx_dir: str = None
    entity_realm_path: str = None
    result_set_metadata: ResultSetMetadata = None