from datatools.dbview.x.util.db_query import DbQuery
from datatools.ev.app_types import View


class ViewDb(View):
    realm: 'RealmPg'
    query: DbQuery

    def __init__(self, realm: 'RealmPg', query: DbQuery) -> None:
        self.realm = realm
        self.query = query

