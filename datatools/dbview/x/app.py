#!/usr/bin/env python3

from datatools.dbview.x.entity_reference import EntityReference, DbRowReference, DbSelectorClause
from datatools.dbview.x.util.pg import get_env, get_where_clauses
from datatools.dbview.x.view_db_row import ViewDbRow
from datatools.util.dataclasses import dataclass_from_dict


def make_view(e_ref: EntityReference):
    if type(e_ref) is DbRowReference:
        return ViewDbRow(e_ref)


def main():
    ref = DbRowReference(table=get_env('TABLE'), selector=[DbSelectorClause(*w) for w in get_where_clauses()])

    while True:
        view = make_view(ref)
        if view is None:
            break

        e_ref, spec = view.run()
        if e_ref is None:
            break

        ref = dataclass_from_dict(
            EntityReference, spec, {'db_row': DbRowReference}
        )


if __name__ == "__main__":
    main()
