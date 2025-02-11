from datatools.dbview.x.util.pg import get_where_clauses
from datatools.ev.app_types import Realm
from datatools.ev.x.db.selector_resolver import resolve_selector
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.types import DbRowReference, DbTableRowsSelector, DbSelectorClause, DbRowsReference


def resolve_pg_entity(realm: Realm, base_path: str, rest: str):
    return DbRowReference(
        realm_name=realm.name,
        selector=resolve_selector(base_path, rest)
    )


def initial_entity_ref(data_source: PgDataSource, realm_name=None):
    where_clauses = get_where_clauses()
    table = data_source.get_env('TABLE')

    if len(where_clauses) == 1 and where_clauses[0][1] == '=':
        return DbRowReference(
            realm_name=realm_name,
            selector=DbTableRowsSelector(
                table=table,
                where=[DbSelectorClause(*w) for w in where_clauses]
            )
        )
    else:
        return DbRowsReference(
            realm_name=realm_name,
            selector=DbTableRowsSelector(
                table=table,
                where=[DbSelectorClause(*w) for w in where_clauses]
            )
        )