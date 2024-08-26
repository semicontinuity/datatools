from typing import List, Optional

from picotui.defs import KEY_ENTER, KEY_F1

from datatools.dbview.util.pg import execute_sql, get_table_foreign_keys_outbound, \
    get_table_foreign_keys_inbound
from datatools.dbview.x.app_highlighting import AppHighlighting
from datatools.dbview.x.app_tree_structure import JsonTreeStructure
from datatools.dbview.x.get_referring_rows import make_referring_rows_model
from datatools.dbview.x.types import DbRowReference, DbSelectorClause, EntityReference, View, DbReferrers, \
    DbTableRowsSelector
from datatools.dbview.x.util.pg import connect_to_db
from datatools.json.util import to_jsonisable
from datatools.jv.app import loop, make_document
from datatools.jv.highlighting.holder import set_current_highlighting, get_current_highlighting
from datatools.tui.screen_helper import with_alternate_screen
from datatools.util.logging import debug


class ViewDbRow(View):
    selector: DbTableRowsSelector

    def __init__(self, selector: DbTableRowsSelector) -> None:
        self.selector = selector

    def run(self) -> Optional[EntityReference]:
        with connect_to_db() as conn:
            self.refresh_model(conn)
            tree = self.make_repr_tree()
            doc = make_document(tree)
            key_code, cur_line = with_alternate_screen(lambda: loop(doc))
            return self.handle_loop_result(doc, key_code, cur_line)

    def make_repr_tree(self):
        return {
            "ENTITY": {
                "metadata": {
                    "self": {
                        "table": self.selector.table,
                        "selector": [
                            {
                                "column": clause.column,
                                "op": clause.op,
                                "value": clause.value
                            } for clause in self.selector.where
                        ]
                    }
                },
                "data": self.data,
                "concepts": {
                    self.selector.table: {
                        "references": self.references
                    }
                }
            }
        }

    def get_entity_row(self, conn, table: str, where: List[DbSelectorClause]):
        if not where:
            raise Exception('WHERE clause is required')
        if len(where) != 1:
            raise Exception('WHERE clauses must contain 1 clause')

        where_column, where_op, where_value = where[0].column, where[0].op, where[0].value
        if where_op != '=':
            raise Exception('WHERE clause must be PK equality')

        sql = f"SELECT * from {table} where {where_column} {where_op} {where_value}"
        debug(sql)
        rows = execute_sql(conn, sql)
        if len(rows) != 1:
            raise Exception(f'illegal state: expected 1 row, but was {len(rows)}')
        return rows[0]

    def refresh_model(self, conn):
        table = self.selector.table
        selector = self.selector.where
        self.data = {
            "self": to_jsonisable(self.get_entity_row(conn, table, selector)),
        }
        inbound_relations = get_table_foreign_keys_inbound(conn, table)
        in_refs_model = make_referring_rows_model(conn, table, selector, inbound_relations)
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

    def handle_loop_result(self, document, key_code, cur_line: int) -> Optional[EntityReference]:
        if key_code == KEY_ENTER:
            path = document.selected_path(cur_line)
            value = document.selected_value(cur_line)
            if JsonTreeStructure.path_is_pk_element(path):
                return DbRowReference(
                    DbTableRowsSelector(
                        table=JsonTreeStructure.get_referring_table(path),
                        where=[DbSelectorClause(JsonTreeStructure.get_pk_value(path), '=', f"'{value}'")]
                    )
                )
            elif get_current_highlighting().is_fk(path):
                fk_field_name = JsonTreeStructure.self_field_name(path)
                referred = self.references[fk_field_name]
                return DbRowReference(
                    DbTableRowsSelector(
                        table=referred['concept'],
                        where=[DbSelectorClause(referred['concept-pk'], '=', f"'{value}'")]
                    )
                )
        elif key_code == KEY_F1:
            return DbReferrers(self.selector)
