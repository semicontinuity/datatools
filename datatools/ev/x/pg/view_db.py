import json

from datatools.dbview.x.util.db_query import DbQuery
from datatools.dbview.x.util.db_query import DbQuerySelector, DbQuerySelectorResolve
from datatools.ev.app_types import View
from datatools.ev.x.pg.db_entity_data import DbEntityData
from datatools.ev.x.pg.types import DbRowReference
from datatools.json.util import to_jsonisable
from datatools.tui.popup_selector import choose
from datatools.util.object_exporter import ObjectExporter


class ViewDb(View):
    realm: 'RealmPg'
    query: DbQuery
    db_entity_data: DbEntityData

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
                alias=f'{referred_table}_{referred_table_field}',
            )
        ) if s.column == column_key else s

    def export_entity(self):
        ObjectExporter.INSTANCE.export(
            str(
                json.dumps(
                    to_jsonisable(
                        self.query,
                    )
                )
            ),
            {
                "Content-Type": "application/x-basic-entity",
                "X-Realm-Ctx": self.db_entity_data.realm_ctx,
                "X-Realm-Ctx-Dir": self.db_entity_data.realm_ctx_dir,
                "X-Entity-Realm-Path": self.db_entity_data.entity_realm_path,
            },
            0
        )

    def export_entity2(self):
        ObjectExporter.INSTANCE.export(
            {
                "realm-ctx": self.db_entity_data.realm_ctx,
                "realm-ctx-dir": self.db_entity_data.realm_ctx_dir,
                'query': json.dumps(to_jsonisable(self.query)),
                'data': '\n'.join(json.dumps(to_jsonisable(r)) for r in self.db_entity_data.rows)
            },
            {
                "Content-Type": "multipart/form-data",
            },
            0
        )
