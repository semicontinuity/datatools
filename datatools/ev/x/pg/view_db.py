from datatools.dbview.x.util.db_query import DbQuery
from datatools.ev.app_types import View
from datatools.ev.x.pg.db_entity_data import DbEntityData


class ViewDb(View):
    realm: 'RealmPg'
    query: DbQuery

    def __init__(self, realm: 'RealmPg', query: DbQuery) -> None:
        self.realm = realm
        self.query = query

    # @abstract
    def build_for_db_entity_data(self, db_entity_data: DbEntityData):
        ...
