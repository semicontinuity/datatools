#!/usr/bin/env python3
from typing import Tuple, Hashable, List, Dict

from picotui.defs import KEY_ENTER

from datatools.dbview.util.pg import execute_sql, get_table_foreign_keys_outbound, \
    get_table_foreign_keys_inbound
from datatools.dbview.x.app_highlighting import AppHighlighting
from datatools.dbview.x.get_referring_rows import make_referring_rows_model
from datatools.dbview.x.util.pg import get_env, get_where_clauses, connect_to_db
from datatools.json.util import to_jsonisable
from datatools.jv.app import loop, make_document
from datatools.jv.highlighting.highlighting import Highlighting
from datatools.tui.screen_helper import with_alternate_screen
from datatools.util.logging import debug


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


def get_entity_row(conn, table: str, where: List[Tuple[str, str, str]]):
    if not where:
        raise Exception('WHERE clause is required')
    if len(where) != 1:
        raise Exception('WHERE clauses must contain 1 clause')

    where_column, where_op, where_value = where[0]
    if where_op != '=':
        raise Exception('WHERE clause must be PK equality')

    sql = f"SELECT * from {table} where {where_column} {where_op} {where_value}"
    debug(sql)
    rows = execute_sql(conn, sql)
    if len(rows) != 1:
        raise Exception(f'illegal state: expected 1 row, but was {len(rows)}')
    return rows[0]


def foreign_keys_outbound_to_concept(table_foreign_keys_outbound: List[Dict]):
    references = {}
    for entry in table_foreign_keys_outbound:
        references[entry['column_name']] = {
            'concept': entry['foreign_table_name'],
            'concept-pk': entry['foreign_column_name'],
        }
    return {
        "references": references
    }


def main():
    Highlighting.CURRENT = AppHighlighting()

    table = get_env('TABLE')
    where = get_where_clauses()

    with connect_to_db() as conn:
        while True:
            data = {
                "self": to_jsonisable(get_entity_row(conn, table, where)),
            }

            inbound_relations = get_table_foreign_keys_inbound(conn, table)
            in_refs_model = make_referring_rows_model(conn, table, where, inbound_relations)
            if len(in_refs_model) > 0:
                data["referrers"] = in_refs_model

            model = {
                "ENTITY": {
                    "metadata": {
                        "self": {
                            "table": table,
                            "selector": [
                                {
                                    "column": e[0],
                                    "op": e[1],
                                    "value": e[2]
                                } for e in where
                            ]
                        }
                    },
                    "data": data,
                    "concepts": {
                        table: foreign_keys_outbound_to_concept(get_table_foreign_keys_outbound(conn, table))
                    }
                }
            }

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
