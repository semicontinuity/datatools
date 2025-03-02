from datatools.dbview.x.util.db_query import DbQuery
from datatools.dbview.x.util.db_query import DbQuerySelector, DbQuerySelectorResolve
from datatools.ev.app_types import View
from datatools.ev.x.pg.db_entity_data import DbEntityData
from datatools.ev.x.pg.types import DbRowReference
from datatools.tui.popup_selector import choose


class ViewDb(View):
    realm: 'RealmPg'
    query: DbQuery

    def __init__(self, realm: 'RealmPg', query: DbQuery) -> None:
        self.realm = realm
        self.query = query

    # @abstract
    def build_for_db_entity_data(self, db_entity_data: DbEntityData):
        ...

    def table_selectors(self) -> list[DbQuerySelector]:
        return self.db_entity_data.query.selectors or [DbQuerySelector(column=c) for c in self.realm.table_fields(self.db_entity_data.query.table)]

    def referred_table(self, field: str):
        c = self.db_entity_data.references.get(field)
        if c is None:
            return None
        return c['concept']

    def table_fields(self, table: str):
        return self.realm.table_fields(table)

    def resolved_column_entity_ref(self, column_key):
        referred_table = self.referred_table(column_key)
        if referred_table is None:
            return
        referred_table_fields = self.table_fields(referred_table)
        referred_table_field_index = choose(referred_table_fields, f'Choose a field from {self.query.table}')
        if referred_table_field_index is None:
            return
        referred_table_field = referred_table_fields[referred_table_field_index]

        return DbRowReference(
            realm_name=self.realm.name,
            selector=None,
            query=self.db_entity_data.query.with_selectors(
                [
                    self.replace_selector_with_lookup(s, column_key, referred_table, referred_table_field)
                    for s in self.table_selectors()
                ]
            )
        )

    def replace_selector_with_lookup(self, s: DbQuerySelector, column_key: str, referred_table: str, referred_table_field: str) -> DbQuerySelector:
        return DbQuerySelector(
            column=column_key,
            resolve=DbQuerySelectorResolve(
                table=referred_table,
                select=referred_table_field,
                column=column_key, # pass PK!
                alias=referred_table,
            )
        ) if s.column == column_key else s
