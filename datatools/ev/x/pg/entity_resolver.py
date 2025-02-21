import os

from datatools.dbview.util.pg import get_table_pks
from datatools.dbview.x.util.pg import get_where_clauses_from_props
from datatools.ev.app_types import EntityReference
from datatools.ev.x.db.selector_resolver import resolve_table_and_clauses
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.realm_pg import RealmPg
from datatools.ev.x.pg.types import DbTableRowsSelector, DbSelectorClause, DbRowsReference, DbRowReference


def resolve_pg_entity(realm: RealmPg, base_path: str, rest: str) -> EntityReference:
    table, where_clauses = resolve_table_and_clauses(base_path, rest)
    return initial_entity_ref_for(realm.name, table, where_clauses, realm.data_source)


def initial_entity_ref(data_source: PgDataSource, realm_name=None) -> EntityReference:
    table = data_source.get_env('TABLE')
    where_clauses = get_where_clauses_from_props(os.environ)
    return initial_entity_ref_for(realm_name, table, where_clauses, data_source)


def initial_entity_ref_for(realm_name: str, table: str, where_clauses, data_source: PgDataSource):
    clauses = [DbSelectorClause(*w) for w in where_clauses]

    return DbRowReference(
        realm_name=realm_name,
        selector=DbTableRowsSelector(
            table=table,
            where=clauses
        )
    ) if has_clause_with_pk(data_source, table, where_clauses) else \
        DbRowsReference(
            realm_name=realm_name,
            selector=DbTableRowsSelector(
                table=table,
                where=clauses
            ),
            query=None
        )


def has_clause_with_pk(data_source: PgDataSource, table: str, where_clauses: list[tuple[str, str, str]]):
    with data_source.connect_to_db() as conn:
        pks = get_table_pks(conn, table)

        count = 0
        for pk in pks:
            if __has_clause_with_pk(pk, where_clauses):
                count += 1
        return count == len(pk)


def __has_clause_with_pk(pk: str, where_clauses: list[tuple[str, str, str]]):
    matches = [where_clause for where_clause in where_clauses if where_clause[0] == pk]
    return len(matches) == 1 and matches[0][1] == '='
