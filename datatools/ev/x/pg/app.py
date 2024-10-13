#!/usr/bin/env python3
import json
import os
from typing import Dict

from datatools.dbview.x.util.pg import get_where_clauses
from datatools.ev.app_support import run_app
from datatools.ev.app_types import Realm
from datatools.ev.x.pg.realm_pg import RealmPg
from datatools.ev.x.pg.types import DbRowReference, DbSelectorClause, DbTableRowsSelector


def get_env(key):
    value = os.getenv(key)
    if value is None:
        raise Exception(f'Must set {key}')
    return value


def links(p):
    if p is None:
        return {}
    else:
        return json.loads(p)


def realms() -> Dict[str, Realm]:
    return {
        None: RealmPg(
            None,
            get_env('HOST'),
            get_env('PORT'),
            get_env('DB_NAME'),
            get_env('DB_USER'),
            get_env('PASSWORD'),
            links(os.getenv('LINKS'))
        )
    }


def main():
    run_app(
        realms(),
        DbRowReference(
            realm_name=None,
            selector=DbTableRowsSelector(
                table=get_env('TABLE'),
                where=[DbSelectorClause(*w) for w in get_where_clauses()]
            )
        )
    )


if __name__ == "__main__":
    main()
