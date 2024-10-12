#!/usr/bin/env python3

from datatools.ev.x.pg.types import EntityReference, DbRowReference, DbSelectorClause, DbReferrers, \
    DbTableRowsSelector
from datatools.dbview.x.util.pg import get_env, get_where_clauses
from datatools.ev.x.pg.view_db_referrers import ViewDbReferrers2
from datatools.ev.x.pg.view_db_row import ViewDbRow
from datatools.ev.app_support import run_app, View


def main():
    ref = DbRowReference(
        DbTableRowsSelector(
            table=get_env('TABLE'),
            where=[DbSelectorClause(*w) for w in get_where_clauses()]
        )
    )

    run_app(ref, create_view)


def create_view(e_ref: EntityReference) -> View:
    if type(e_ref) is DbRowReference:
        return ViewDbRow(e_ref.selector)
    elif type(e_ref) is DbReferrers:
        return ViewDbReferrers2(e_ref.selector)


if __name__ == "__main__":
    main()
