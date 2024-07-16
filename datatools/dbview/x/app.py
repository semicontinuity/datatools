#!/usr/bin/env python3
from typing import Tuple, Hashable, List

from picotui.defs import KEY_ENTER

from datatools.dbview.x.get_referring_rows import referring_rows_model
from datatools.dbview.x.util.pg import get_env, get_where_clauses
from datatools.jv.app import loop, make_document
from datatools.tui.screen_helper import with_alternate_screen


def data():
    table = get_env('TABLE')
    where = get_where_clauses()
    model = referring_rows_model(table, where)
    return model


def handle_loop_result(document, key_code, cur_line: int) -> Tuple[bool, str, List[Hashable]]:
    if key_code == KEY_ENTER:
        path = document.selected_path(cur_line)
        value = document.selected_value(cur_line)
        is_leaf = type(value) is str
        if is_leaf and path[3] == 'key':
            return True, value, path
    return False, "", []


def main():

    table = get_env('TABLE')
    where = get_where_clauses()

    while True:
        model = referring_rows_model(table, where)
        doc = make_document(model)
        key_code, cur_line = with_alternate_screen(lambda: loop(doc))
        is_leaf, value, path = handle_loop_result(doc, key_code, cur_line)
        if is_leaf:
            # print('is_leaf', is_leaf, path[3])
            table = path[0]
            where = [(path[4], '=', f"'{value}'")]
            continue
        break


if __name__ == "__main__":
    main()
