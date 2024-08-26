#!/usr/bin/env python3

from datatools.dbview.x.types import EntityReference, DbRowReference, DbSelectorClause, DbReferrers, View, \
    DbTableRowsSelector, DbReferringRows
from datatools.dbview.x.util.pg import get_env, get_where_clauses
from datatools.dbview.x.view_db_referrers import ViewDbReferrers
from datatools.dbview.x.view_db_referring_rows import ViewDbReferringRows
from datatools.dbview.x.view_db_row import ViewDbRow


def main():
    ref = DbRowReference(
        DbTableRowsSelector(
            table=get_env('TABLE'),
            where=[DbSelectorClause(*w) for w in get_where_clauses()]
        )
    )

    while True:
        view = make_view(ref)
        if view is None:
            break

        ref = view.run()
        if ref is None:
            break


def make_view(e_ref: EntityReference) -> View:
    if type(e_ref) is DbRowReference:
        return ViewDbRow(e_ref.selector)
    elif type(e_ref) is DbReferrers:
        return ViewDbReferrers(e_ref.selector)
    elif type(e_ref) is DbReferringRows:
        return ViewDbReferringRows(e_ref)


if __name__ == "__main__":
    main()
