from typing import List, Optional, Any

from picotui.defs import KEY_F1

from datatools.dbview.util.pg import get_table_pks
from datatools.dbview.x.util.db_query import DbQuery
from datatools.ev.app_types import EntityReference
from datatools.ev.x.db.element_factory import DbElementFactory
from datatools.ev.x.pg.types import DbSelectorClause, DbReferrers, \
    DbTableRowsSelector
from datatools.ev.x.pg.view_db import ViewDb
from datatools.ev.x.pg.view_db_row_grid import ViewDbRowGrid
from datatools.jv.app import do_loop, make_document_for_model, make_tree_grid
from datatools.jv.jdocument import JDocument
from datatools.jv.jgrid import JGrid
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from datatools.util.logging import debug


class ViewDbRow(ViewDb):
    selector: DbTableRowsSelector
    references: dict[str, Any]
    doc: JDocument
    g: JGrid

    def __init__(self, realm: 'RealmPg', selector: DbTableRowsSelector, query: DbQuery) -> None:
        super().__init__(realm, query)
        self.selector = selector

    # @override
    def build(self):
        with self.realm.connect_to_db() as conn:
            self.references = self.realm.make_references(conn, self.selector.table)
            self.table_pks = get_table_pks(conn, self.selector.table)

            j = self.get_entity_row(conn, self.selector.table, self.selector.where)

            factory = DbElementFactory()
            j_object = factory.build_row_view(
                j,
                self.references,
                self.table_pks,
                self.realm.links.get(self.selector.table) or {},
                self.realm,
            )
            footer = self.selector.table + ' ' + ' '.join([w.column + w.op + w.value for w in self.selector.where])

            self.doc = make_document_for_model(factory.set_indent_recursive(j_object), j, footer)
            self.g = make_tree_grid(self.doc, with_alternate_screen(lambda: screen_size_or_default()), ViewDbRowGrid)

    # @override
    def run(self) -> Optional[EntityReference]:
        loop_result, cur_line = with_alternate_screen(lambda: do_loop(self.g))
        return self.handle_loop_result(self.doc, loop_result, cur_line)

    def handle_loop_result(self, document, loop_result, cur_line: int) -> Optional[EntityReference]:
        if loop_result == KEY_F1:
            return DbReferrers(realm_name=self.realm.name, selector=self.selector)
        else:
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
