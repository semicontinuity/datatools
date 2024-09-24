#!/usr/bin/env python3

from datatools.dbview.share.app_support import run_app, View
from datatools.dbview.x.types import EntityReference, DbRowReference, DbSelectorClause, DbReferrers, \
    DbTableRowsSelector, DbReferringRows
from datatools.dbview.x.util.pg import get_env, get_where_clauses
from datatools.dbview.x.view_db_referrers2 import ViewDbReferrers2
from datatools.dbview.x.view_db_referring_rows import ViewDbReferringRows
from datatools.dbview.x.view_db_row import ViewDbRow


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
    elif type(e_ref) is DbReferringRows:
        return ViewDbReferringRows(e_ref)


if __name__ == "__main__":
    main()
