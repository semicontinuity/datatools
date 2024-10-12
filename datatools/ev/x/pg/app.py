#!/usr/bin/env python3
import os
from typing import Dict

from datatools.dbview.x.util.pg import get_where_clauses
from datatools.ev.app_support import run_app, View
from datatools.ev.app_types import Realm
from datatools.ev.x.pg.realm_pg import RealmPg
from datatools.ev.x.pg.types import EntityReference, DbRowReference, DbSelectorClause, DbTableRowsSelector


def get_env(key):
    value = os.getenv(key)
    if value is None:
        raise Exception(f'Must set {key}')
    return value


realm = RealmPg(
    None,
    get_env('HOST'),
    get_env('PORT'),
    get_env('DB_NAME'),
    get_env('DB_USER'),
    get_env('PASSWORD'),
)
realms: Dict[str, Realm] = {None: realm}


def main():
    ref = DbRowReference(
        realm_name=None,
        selector=DbTableRowsSelector(
            table=get_env('TABLE'),
            where=[DbSelectorClause(*w) for w in get_where_clauses()]
        )
    )

    run_app(realms, ref, create_view)


def create_view(e_ref: EntityReference) -> View:
    if isinstance(e_ref, EntityReference):
        return realms[e_ref.realm_name].create_view(e_ref)


if __name__ == "__main__":
    main()
