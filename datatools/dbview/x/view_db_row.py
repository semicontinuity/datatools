import sys
from dataclasses import dataclass
from typing import Tuple, Sequence

from picotui.defs import KEY_ENTER

from datatools.dbview.util.pg import execute_sql, get_table_foreign_keys_outbound, \
    get_table_foreign_keys_inbound
from datatools.dbview.x.app_highlighting import AppHighlighting
from datatools.dbview.x.app_tree_structure import JsonTreeStructure
from datatools.dbview.x.get_referring_rows import make_referring_rows_model
from datatools.dbview.x.util.pg import connect_to_db
from datatools.json.util import to_jsonisable
from datatools.jv.app import loop, make_document
from datatools.jv.highlighting.holder import set_current_highlighting, get_current_highlighting
from datatools.tui.screen_helper import with_alternate_screen
from datatools.util.logging import debug


@dataclass
class DbEntityReference:
    table: str
    where: Sequence[Tuple[str, str, str]]


class ViewDbRow:
    e_ref: DbEntityReference

    def __init__(self, e_ref: DbEntityReference) -> None:
        self.e_ref = e_ref

    def run(self):
        while True:
            with connect_to_db() as conn:
                self.refresh_model(conn)
                doc = make_document(self.make_repr_tree())
                key_code, cur_line = with_alternate_screen(lambda: loop(doc))
                self.e_ref = self.handle_loop_result(doc, key_code, cur_line)
                if self.e_ref is None:
                    break

    def make_repr_tree(self):
        return {
            "ENTITY": {
                "metadata": {
                    "self": {
                        "table": self.e_ref.table,
                        "selector": [
                            {
                                "column": e[0],
                                "op": e[1],
                                "value": e[2]
                            } for e in self.e_ref.where
                        ]
                    }
                },
                "data": self.data,
                "concepts": {
                    self.e_ref.table: {
                        "references": self.references
                    }
                }
            }
        }

    def handle_loop_result(self, document, key_code, cur_line: int) -> DbEntityReference:
        if key_code == KEY_ENTER:
            path = document.selected_path(cur_line)
            value = document.selected_value(cur_line)
            if JsonTreeStructure.path_is_pk_element(path):
                return DbEntityReference(
                    table=JsonTreeStructure.get_referring_table(path),
                    where=[(JsonTreeStructure.get_pk_value(path), '=', f"'{value}'")]
                )
            elif get_current_highlighting().is_fk(path):
                fk_field_name = JsonTreeStructure.self_field_name(path)
                referred = self.references[fk_field_name]
                return DbEntityReference(
                    table=referred['concept'],
                    where=[(referred['concept-pk'], '=', f"'{value}'")]
                )

    def get_entity_row(self, conn, table: str, where: Sequence[Tuple[str, str, str]]):
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

    def refresh_model(self, conn):
        table = self.e_ref.table
        where = self.e_ref.where
        self.data = {
            "self": to_jsonisable(self.get_entity_row(conn, table, where)),
        }
        inbound_relations = get_table_foreign_keys_inbound(conn, table)
        in_refs_model = make_referring_rows_model(conn, table, where, inbound_relations)
        if len(in_refs_model) > 0:
            self.data["referrers"] = in_refs_model
        outbound_relations = get_table_foreign_keys_outbound(conn, table)
        self.references = {
            entry['column_name']: {
                'concept': entry['foreign_table_name'],
                'concept-pk': entry['foreign_column_name'],
            }
            for entry in outbound_relations
        }
        set_current_highlighting(AppHighlighting(self.references))
