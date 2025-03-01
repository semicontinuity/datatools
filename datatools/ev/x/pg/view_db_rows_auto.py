from datatools.dbview.x.util.db_query import DbQuery
from datatools.ev.app_types import EntityReference
from datatools.ev.x.pg.types import DbTableRowsSelector
from datatools.ev.x.pg.view_db import ViewDb
from datatools.ev.x.pg.view_db_row import ViewDbRow
from datatools.ev.x.pg.view_db_rows import ViewDbRows


class ViewDbRowsAuto(ViewDb):

    def __init__(self, realm: 'RealmPg', selector: DbTableRowsSelector, query: DbQuery) -> None:
        super().__init__(realm, query)
        self.selector = selector

    # @override
    def build(self):
        with self.realm.connect_to_db() as conn:
            db_entity_data = self.realm.db_entity_data(conn, self.query)

        if len(db_entity_data.rows) == 1:
            self.delegate = ViewDbRow(self.realm, self.selector, self.query)
        else:
            self.delegate = ViewDbRows(self.realm, self.query)

        self.delegate.build_for_db_entity_data(db_entity_data)

    # @override
    def run(self) -> EntityReference|None:
        return self.delegate.run()
