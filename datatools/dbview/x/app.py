#!/usr/bin/env python3

from datatools.dbview.x.types import EntityReference, DbRowReference, DbSelectorClause, DbReferrers, View, \
    DbTableRowsSelector, DbReferringRows
from datatools.dbview.x.util.pg import get_env, get_where_clauses
from datatools.dbview.x.view_db_referrers2 import ViewDbReferrers2
from datatools.dbview.x.view_db_referring_rows import ViewDbReferringRows
from datatools.dbview.x.view_db_row import ViewDbRow
from datatools.tui.picotui_keys import KEY_ALT_SHIFT_LEFT, KEY_ALT_SHIFT_RIGHT, KEY_ALT_SHIFT_UP


def main():
    ref = DbRowReference(
        DbTableRowsSelector(
            table=get_env('TABLE'),
            where=[DbSelectorClause(*w) for w in get_where_clauses()]
        )
    )

    history = []
    history_idx = 0

    while True:
        view = make_view(ref)
        if view is None:
            if ref == KEY_ALT_SHIFT_LEFT:
                history_idx = max(0, history_idx - 1)
                view = history[history_idx]
            elif ref == KEY_ALT_SHIFT_RIGHT:
                history_idx = min(len(history) - 1, history_idx + 1)
                view = history[history_idx]
            elif ref == KEY_ALT_SHIFT_UP:
                print(history_idx, [type(e) for e in history])
                break
            else:
                break
        else:
            history_idx += 1
            history = history[:history_idx + 1]
            history.append(view)
            history_idx = len(history) - 1

        ref = view.run()
        if ref is None:
            break


def make_view(e_ref: EntityReference) -> View:
    if type(e_ref) is DbRowReference:
        return ViewDbRow(e_ref.selector)
    elif type(e_ref) is DbReferrers:
        return ViewDbReferrers2(e_ref.selector)
    elif type(e_ref) is DbReferringRows:
        return ViewDbReferringRows(e_ref)


if __name__ == "__main__":
    main()
