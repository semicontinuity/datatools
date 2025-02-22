from typing import List, Optional

from datatools.ev.app_types import View, EntityReference
from datatools.ev.x.db.element_factory import DbElementFactory
from datatools.ev.x.pg.types import DbSelectorClause, DbTableRowsSelector
from datatools.jv.app import make_document, make_json_tree_applet_grid, do_loop
from datatools.jv.jdocument import JDocument
from datatools.tui.screen_helper import with_alternate_screen
from datatools.util.logging import debug


class ViewChRow(View):
    realm: 'RealmClickhouse'
    selector: DbTableRowsSelector
    doc: JDocument

    def __init__(self, realm: 'RealmClickhouse', selector: DbTableRowsSelector) -> None:
        self.realm = realm
        self.selector = selector

    def build(self):
        with self.realm.connect_to_db() as conn:
            self.references = {}
            self.table_pks = []

            self.doc = make_document(
                DbElementFactory().build_row_view(
                    self.get_entity_row(conn, self.selector.table, self.selector.where),
                    self.references,
                    self.table_pks,
                    self.realm.links.get(self.selector.table) or {},
                    self.realm,
                ),
                self.selector.table + ' ' + ' '.join([w.column + w.op + w.value for w in self.selector.where])
            )
            self.g = with_alternate_screen(lambda: make_json_tree_applet_grid(self.doc))

    def run(self) -> Optional[EntityReference]:
        loop_result, cur_line = with_alternate_screen(lambda: do_loop(self.g))
        return self.handle_loop_result(self.doc, loop_result, cur_line)

    def handle_loop_result(self, document, loop_result, cur_line: int) -> Optional[EntityReference]:
        return loop_result

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
        rows = self.realm.execute_query(conn, sql)
        if len(rows) != 1:
            raise Exception(f'illegal state: expected 1 row, but was {len(rows)}')
        return rows[0]
