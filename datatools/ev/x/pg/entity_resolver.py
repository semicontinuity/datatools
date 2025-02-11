import os

from datatools.dbview.x.util.pg import get_where_clauses_from_props
from datatools.ev.app_types import Realm, EntityReference
from datatools.ev.x.db.selector_resolver import resolve_table_and_clauses
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.types import DbRowReference, DbTableRowsSelector, DbSelectorClause, DbRowsReference


def resolve_pg_entity(realm: Realm, base_path: str, rest: str) -> EntityReference:
    table, where_clauses = resolve_table_and_clauses(base_path, rest)
    return initial_entity_ref_for(realm.name, table, where_clauses)


def initial_entity_ref(data_source: PgDataSource, realm_name=None) -> EntityReference:
    table = data_source.get_env('TABLE')
    where_clauses = get_where_clauses_from_props(os.environ)
    return initial_entity_ref_for(realm_name, table, where_clauses)


def initial_entity_ref_for(realm_name: str, table: str, where_clauses):
    clauses = [DbSelectorClause(*w) for w in where_clauses]

    return DbRowReference(
        realm_name=realm_name,
        selector=DbTableRowsSelector(
            table=table,
            where=clauses
        )
    ) if len(clauses) == 1 and clauses[0].op == '=' else \
        DbRowsReference(
            realm_name=realm_name,
            selector=DbTableRowsSelector(
                table=table,
                where=clauses
            )
        )
