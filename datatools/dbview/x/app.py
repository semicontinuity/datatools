#!/usr/bin/env python3

from datatools.dbview.x.entity_reference import EntityReference, DbRowReference, DbSelectorClause
from datatools.dbview.x.util.pg import get_env, get_where_clauses
from datatools.dbview.x.view_db_row import ViewDbRow


def make_view(e_ref: EntityReference):
    if type(e_ref) is DbRowReference:
        return ViewDbRow(e_ref)


def main():
    ref = DbRowReference(table=get_env('TABLE'), selector=[DbSelectorClause(*w) for w in get_where_clauses()])

    while True:
        view = make_view(ref)
        if view is None:
            break

        ref = view.run()
        if ref is None:
            break


if __name__ == "__main__":
    main()
