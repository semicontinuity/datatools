#!/usr/bin/env python3
from typing import Tuple, Hashable, List

from picotui.defs import KEY_ENTER

from datatools.dbview.x.get_referring_rows import make_referring_rows_model
from datatools.dbview.x.util.pg import get_env, get_where_clauses, connect_to_db
from datatools.jv.app import loop, make_document
from datatools.tui.screen_helper import with_alternate_screen


class JsonTreeStructure:
    @staticmethod
    def path_is_pk_element(path: List[Hashable]):
        return len(path) == 8 and path[6] == 'key'

    @staticmethod
    def get_pk_value(path: List[Hashable]):
        return path[7]

    @staticmethod
    def get_referring_table(path: List[Hashable]) -> str:
        return path[3]


def handle_loop_result(document, key_code, cur_line: int) -> Tuple[bool, str, List[Hashable]]:
    if key_code == KEY_ENTER:
        path = document.selected_path(cur_line)
        value = document.selected_value(cur_line)
        if JsonTreeStructure.path_is_pk_element(path):
            return True, value, path
    return False, "", []


def main():
    table = get_env('TABLE')
    where = get_where_clauses()

    with connect_to_db() as conn:
        while True:
            in_refs_model = make_referring_rows_model(conn, table, where)
            model = {"ENTITY": {"data": {"referring": in_refs_model}}}
            doc = make_document(model)
            key_code, cur_line = with_alternate_screen(lambda: loop(doc))
            is_leaf, value, path = handle_loop_result(doc, key_code, cur_line)
            if is_leaf:
                table = JsonTreeStructure.get_referring_table(path)
                where = [(JsonTreeStructure.get_pk_value(path), '=', f"'{value}'")]
                continue
            break


if __name__ == "__main__":
    main()
