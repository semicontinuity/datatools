import os
from typing import List, Optional, Dict, Any

from picotui.defs import KEY_ENTER, KEY_F1

from datatools.dbview.util.pg import execute_sql, get_table_foreign_keys_outbound, \
    get_table_foreign_keys_inbound, get_table_pks
from datatools.dbview.x import cleanse_dict
from datatools.dbview.x.app_tree_structure import JsonTreeStructure
from datatools.dbview.x.get_referring_rows import make_referring_rows_model
from datatools.dbview.x.types import DbRowReference, DbSelectorClause, EntityReference, View, DbReferrers, \
    DbTableRowsSelector
from datatools.dbview.x.util.pg import connect_to_db
from datatools.json.util import to_jsonisable
from datatools.jv.app import loop, make_document
from datatools.jv.model import JElementFactory, set_padding
from datatools.jv.model.JObject import JObject
from datatools.jv.model.JString import JString
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.treeview.rich_text import Style
from datatools.util.logging import debug


class JPrimaryKey(JString):
    def value_style(self):
        return Style(AbstractBufferWriter.MASK_BOLD, (64, 160, 192))


class JForeignKey(JString):
    def value_style(self):
        return Style(AbstractBufferWriter.MASK_ITALIC | AbstractBufferWriter.MASK_UNDERLINED, (64, 160, 192))


class ViewDbRow(View):
    selector: DbTableRowsSelector

    def __init__(self, selector: DbTableRowsSelector) -> None:
        self.selector = selector

    def build_row_view(self, model: Dict, references: Dict[str, Any], table_pks: List[str]) -> JObject:
        factory = JElementFactory()

        views = []
        for k, v in model.items():
            if type(v) is str and k in table_pks:
                views.append(JPrimaryKey(v, k))
            elif type(v) is str and k in references:
                views.append(JForeignKey(v, k))
            else:
                views.append(factory.build_model(v, k))

        return JObject(model, None, set_padding(views))

    def run(self) -> Optional[EntityReference]:
        with connect_to_db() as conn:
            self.references = self.make_references(conn)
            self.table_pks = get_table_pks(conn, self.selector.table)

            tree = {
                "ENTITY": {
                    # "metadata": {
                    #     "self": {
                    #         "table": self.selector.table,
                    #         "selector": [
                    #             {
                    #                 "column": clause.column,
                    #                 "op": clause.op,
                    #                 "value": clause.value
                    #             } for clause in self.selector.where
                    #         ]
                    #     }
                    # },
                    "data": cleanse_dict(
                        {
                            "self": self.build_row_view(self.make_row_model(conn), self.references, self.table_pks),
                            "referrers": self.make_inbound_references_models(conn),
                        }
                    ),
                    # "concepts": {
                    #     self.selector.table: {
                    #         "references": self.references
                    #     }
                    # }
                }
            }
            doc = make_document(tree)
            key_code, cur_line = with_alternate_screen(lambda: loop(doc))
            return self.handle_loop_result(doc, key_code, cur_line)

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

    def make_inbound_references_models(self, conn):
        if os.environ.get('IR') is not None:
            inbound_relations = get_table_foreign_keys_inbound(conn, self.selector.table)
            return make_referring_rows_model(conn, self.selector.table, self.selector.where, inbound_relations)

    def make_references(self, conn) -> Dict[str, Any]:
        outbound_relations = get_table_foreign_keys_outbound(conn, self.selector.table)
        references = {
            entry['column_name']: {
                'concept': entry['foreign_table_name'],
                'concept-pk': entry['foreign_column_name'],
            }
            for entry in outbound_relations
        }
        return references

    def make_row_model(self, conn):
        return to_jsonisable(self.get_entity_row(conn, self.selector.table, self.selector.where))

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
            elif self.is_fk(path):
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

    def is_fk(self, path):
        return JsonTreeStructure.is_self_field_name(path) and JsonTreeStructure.self_field_name(path) in self.references

    def is_pk(self, path):
        return JsonTreeStructure.is_self_field_name(path) and JsonTreeStructure.self_field_name(path) in self.table_pks
