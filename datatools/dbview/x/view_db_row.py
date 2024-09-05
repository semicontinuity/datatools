from typing import List, Optional

from picotui.defs import KEY_F1

from datatools.dbview.util.pg import execute_sql, get_table_pks
from datatools.dbview.x.types import DbSelectorClause, EntityReference, View, DbReferrers, \
    DbTableRowsSelector, make_references, MyElementFactory
from datatools.dbview.x.util.pg import connect_to_db
from datatools.jv.app import loop, make_document
from datatools.tui.screen_helper import with_alternate_screen
from datatools.util.logging import debug


class ViewDbRow(View):
    selector: DbTableRowsSelector

    def __init__(self, selector: DbTableRowsSelector) -> None:
        self.selector = selector

    def build(self):
        with connect_to_db() as conn:
            self.references = make_references(conn, self.selector.table)
            self.table_pks = get_table_pks(conn, self.selector.table)

            self.doc = make_document(
                {
                    self.selector.table: MyElementFactory().build_row_view(
                        # to_jsonisable(
                        #     self.get_entity_row(conn, self.selector.table, self.selector.where)
                        # ),
                        self.get_entity_row(conn, self.selector.table, self.selector.where),
                        self.references,
                        self.table_pks
                    )
                }
            )

    def run(self) -> Optional[EntityReference]:
        key_code, cur_line = with_alternate_screen(lambda: loop(self.doc))
        return self.handle_loop_result(self.doc, key_code, cur_line)

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

    def handle_loop_result(self, document, key_code, cur_line: int) -> Optional[EntityReference]:
        if key_code == KEY_F1:
            return DbReferrers(self.selector)
        else:
            return key_code
