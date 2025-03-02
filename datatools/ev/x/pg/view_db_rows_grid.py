import json

from datatools.dbview.x.util.db_query import DbQuerySelector, DbQuerySelectorResolve
from datatools.dbview.x.util.pg_query import query_to_string
from datatools.ev.x.pg.db_entity_data import DbEntityData
from datatools.ev.x.pg.types import DbRowReference
from datatools.json.util import to_jsonisable
from datatools.jt.app.ng.jt_ng_grid import JtNgGrid
from datatools.tui.picotui_keys import *
from datatools.tui.popup_selector import choose
from datatools.util.object_exporter import ObjectExporter


class ViewDbRowsGrid(JtNgGrid):
    db_entity_data: DbEntityData
    document: 'ViewDbRows'

    def handle_edit_key(self, key):
        if key == KEY_SHIFT_F5:
            self.export_json_lines(0, self.data_bundle.orig_data, f'data from {self.db_entity_data.query.table}')
        elif key == KEY_CTRL_ALT_SHIFT_F5:
            ObjectExporter.INSTANCE.export(
                query_to_string(self.db_entity_data.query),
                {"Content-Type": "application/sql"},
                0
            )
        elif key == KEY_CTRL_Q:
            ObjectExporter.INSTANCE.export(
                json.dumps(to_jsonisable(self.db_entity_data.query)),
                {"Content-Type": "application/json"},
                0
            )
        elif key == KEY_CTRL_R:
            column_key = self.column_keys[self.cursor_column]

            referred_table = self.document.referred_table(column_key)
            if referred_table is None:
                return

            referred_table_fields = self.document.table_fields(referred_table)
            referred_table_field_index = choose(referred_table_fields, f'Choose a field from {self.document.query.table}')
            if referred_table_field_index is None:
                return
            referred_table_field = referred_table_fields[referred_table_field_index]

            reference = DbRowReference(
                realm_name=self.document.realm.name,
                selector=None,
                query=self.document.db_entity_data.query.with_selectors(
                    [
                        self.replace_selector_with_lookup(s, column_key, referred_table, referred_table_field)
                        for s in self.document.table_selectors()
                    ]
                )
            )
            return reference
        else:
            return super().handle_edit_key(key)

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
