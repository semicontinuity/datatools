from datatools.ev.app_types import Realm
from datatools.ev.x.ch.types import ClickhouseRowEntity, ClickhouseRowsEntity
from datatools.ev.x.db.selector_resolver import resolve_table_and_clauses
from datatools.ev.x.pg.types import DbTableRowsSelector, DbSelectorClause


def resolve_ch_entity(realm: Realm, base_path: str, rest: str):
    table, where_clauses = resolve_table_and_clauses(base_path, rest)
    return initial_entity_ref_for(realm.name, table, where_clauses)


def initial_entity_ref_for(realm_name: str, table: str, where_clauses):
    clauses = [DbSelectorClause(*w) for w in where_clauses]

    return ClickhouseRowEntity(
        realm_name=realm_name,
        selector=DbTableRowsSelector(
            table=table,
            where=clauses
        )
    ) if len(clauses) == 1 and clauses[0].op == '=' else \
        ClickhouseRowsEntity(
            realm_name=realm_name,
            selector=DbTableRowsSelector(
                table=table,
                where=clauses
            )
        )
