#!/usr/bin/env python3
import json
import os
from typing import Dict

from datatools.dbview.x.util.pg import get_where_clauses
from datatools.ev.app_support import run_app
from datatools.ev.app_types import Realm
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.realm_pg import RealmPg
from datatools.ev.x.pg.types import DbRowReference, DbSelectorClause, DbTableRowsSelector, DbRowsReference


data_source = PgDataSource(os.environ)


def load_links(p):
    if p is None:
        return {}
    else:
        return json.loads(p)


def realms() -> Dict[str, Realm]:
    links = load_links(os.getenv('LINKS'))
    return {
        None: RealmPg(
            None,
            data_source,
            links
        )
    }


def main():
    run_app(
        realms(),
        initial_entity_ref()
    )


def initial_entity_ref():
    where_clauses = get_where_clauses()
    table = data_source.get_env('TABLE')

    if len(where_clauses) == 1 and where_clauses[0][1] == '=':
        return DbRowReference(
            realm_name=None,
            selector=DbTableRowsSelector(
                table=table,
                where=[DbSelectorClause(*w) for w in where_clauses]
            )
        )
    else:
        return DbRowsReference(
            realm_name=None,
            selector=DbTableRowsSelector(
                table=table,
                where=[DbSelectorClause(*w) for w in where_clauses]
            )
        )


if __name__ == "__main__":
    main()
