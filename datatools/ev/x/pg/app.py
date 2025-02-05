#!/usr/bin/env python3
import json
import os
from typing import Dict

from datatools.dbview.x.util.pg import get_where_clauses
from datatools.ev.app_support import run_app
from datatools.ev.app_types import Realm
from datatools.ev.x.pg.realm_pg_x import PgPropertySource
from datatools.ev.x.pg.types import DbRowReference, DbSelectorClause, DbTableRowsSelector, DbRowsReference


property_source = PgPropertySource(os.environ)


def links(p):
    if p is None:
        return {}
    else:
        return json.loads(p)


def realms() -> Dict[str, Realm]:
    return {
        None: property_source.realm_pg(name=None, links=links(os.getenv('LINKS')))
    }


def main():
    run_app(
        realms(),
        initial_entity_ref()
    )


def initial_entity_ref():
    where_clauses = get_where_clauses()
    table = property_source.get_env('TABLE')

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
