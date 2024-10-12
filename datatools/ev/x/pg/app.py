#!/usr/bin/env python3
import os

from datatools.dbview.x.util.pg import get_where_clauses
from datatools.ev.app_support import run_app, View
from datatools.ev.x.pg.realm_pg import RealmPg
from datatools.ev.x.pg.types import EntityReference, DbRowReference, DbSelectorClause, DbReferrers, \
    DbTableRowsSelector
from datatools.ev.x.pg.view_db_referrers import ViewDbReferrers
from datatools.ev.x.pg.view_db_row import ViewDbRow


def get_env(key):
    value = os.getenv(key)
    if value is None:
        raise Exception(f'Must set {key}')
    return value


realm = RealmPg(
    get_env('HOST'),
    get_env('PORT'),
    get_env('DB_NAME'),
    get_env('DB_USER'),
    get_env('PASSWORD'),
)
realms = {None: realm}


def main():
    ref = DbRowReference(
        realm_name=None,
        selector=DbTableRowsSelector(
            table=get_env('TABLE'),
            where=[DbSelectorClause(*w) for w in get_where_clauses()]
        )
    )

    run_app({}, ref, create_view)


def create_view(e_ref: EntityReference) -> View:
    if type(e_ref) is DbRowReference:
        return ViewDbRow(realms[e_ref.realm_name], e_ref.selector)
    elif type(e_ref) is DbReferrers:
        return ViewDbReferrers(realms[e_ref.realm_name], e_ref.selector)


if __name__ == "__main__":
    main()
