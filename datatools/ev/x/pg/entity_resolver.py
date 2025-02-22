import os

from datatools.dbview.util.pg import get_table_pks
from datatools.dbview.x.util.db_query import DbQuery, DbQueryFilterClause
from datatools.dbview.x.util.helper import get_required_prop
from datatools.dbview.x.util.pg import get_where_clauses_from_props, get_where_clauses0
from datatools.dbview.x.util.pg_inferred_query import inferred_query, get_where_clauses1
from datatools.ev.app_types import EntityReference
from datatools.ev.x.db.selector_resolver import table_and_the_rest
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.realm_pg import RealmPg
from datatools.ev.x.pg.types import DbTableRowsSelector, DbSelectorClause, DbRowsReference, DbRowReference


def resolve_pg_entity(realm: RealmPg, base_path: str, rest: str) -> EntityReference:
    table, the_rest = table_and_the_rest(rest)
    where_clauses = get_where_clauses0(base_path + '/' + table, the_rest)

    clauses = get_where_clauses1(base_path, rest)
    query = DbQuery(
        table=get_required_prop('TABLE', os.environ),
        filter=[
            DbQueryFilterClause(
                column=column,
                op=op,
                value=value,
            ) for column, op, value in clauses
        ]
    )

    return initial_entity_ref_for(realm.name, table, where_clauses, realm.data_source, query)


def initial_entity_ref(data_source: PgDataSource, realm_name=None) -> EntityReference:
    table = data_source.get_env('TABLE')
    where_clauses = get_where_clauses_from_props(os.environ)
    query = inferred_query(os.environ)
    return initial_entity_ref_for(realm_name, table, where_clauses, data_source, query)


def initial_entity_ref_for(
        realm_name: str,
        table: str,
        where_clauses,
        data_source: PgDataSource,
        query: DbQuery,
):
    clauses = [DbSelectorClause(*w) for w in where_clauses]

    return DbRowReference(
        realm_name=realm_name,
        selector=DbTableRowsSelector(
            table=table,
            where=clauses
        ),
        query=query
    ) if has_clause_with_pk(data_source, table, where_clauses) else \
        DbRowsReference(
            realm_name=realm_name,
            selector=DbTableRowsSelector(
                table=table,
                where=clauses
            ),
            query=query,
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
