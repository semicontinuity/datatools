from typing import Optional

from datatools.dbview.x.util.db_query import DbQuery
from datatools.ev.app_types import EntityReference
from datatools.ev.x.db.element_factory import DbElementFactory
from datatools.ev.x.pg.db_entity_data import DbEntityData
from datatools.ev.x.pg.types import DbReferrers, \
    DbTableRowsSelector, DbReferringTables
from datatools.ev.x.pg.view_db import ViewDb
from datatools.ev.x.pg.view_db_row_grid import ViewDbRowGrid
from datatools.jv.app import do_loop, make_document_for_model, make_tree_grid
from datatools.jv.jdocument import JDocument
from datatools.jv.jgrid import JGrid
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from picotui.defs import KEY_F1, KEY_F2


class ViewDbRow(ViewDb):
    selector: DbTableRowsSelector
    doc: JDocument
    g: JGrid

    def __init__(self, realm: 'RealmPg', selector: DbTableRowsSelector, query: DbQuery) -> None:
        super().__init__(realm, query)
        self.selector = selector

    # @override
    def build_for_db_entity_data(self, db_entity_data: DbEntityData):
        self.db_entity_data = db_entity_data

        if len(self.db_entity_data.rows) != 1:
            raise Exception(f'illegal state: expected 1 row, but was {len(self.db_entity_data.rows)}')
        j = self.db_entity_data.rows[0]

        factory = DbElementFactory()
        j_object = factory.build_row_view(
            j,
            self.db_entity_data.references,
            self.db_entity_data.pks,
            self.realm.links.get(self.query.table) or {},
            self.realm,
        )
        footer = self.query.table + ' ' + ' '.join([f.column + f.op + f.value for f in self.query.filter])
        self.doc = make_document_for_model(factory.set_indent_recursive(j_object), j, footer)
        self.g = make_tree_grid(self.doc, with_alternate_screen(lambda: screen_size_or_default()), ViewDbRowGrid)
        self.doc.query = self.query
        self.doc.db_entity_data = self.db_entity_data
        self.doc.doc = self

    # @override
    def run(self) -> Optional[EntityReference]:
        loop_result, cur_line = with_alternate_screen(lambda: do_loop(self.g))
        return self.handle_loop_result(self.doc, loop_result, cur_line)

    def handle_loop_result(self, document, loop_result, cur_line: int) -> Optional[EntityReference]:
        if loop_result == KEY_F1:
            # TODO
            return DbReferrers(realm_name=self.realm.name, selector=self.selector, query=self.query)
        elif loop_result == KEY_F2:
            # TODO
            return DbReferringTables(realm_name=self.realm.name, selector=self.selector, query=self.query)
        else:
            return loop_result
