import json

from datatools.dbview.x.util.db_query import DbQuery
from datatools.dbview.x.util.pg_query import query_to_string
from datatools.ev.x.pg.db_entity_data import DbEntityData
from datatools.ev.x.pg.types import DbRowReference, DbTableRowsSelector
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
            referred_table_field = choose(referred_table_fields, f'Choose a field from {self.document.query.table}')
            if referred_table_field is None:
                return

            reference = DbRowReference(
                realm_name=self.document.realm.name,
                selector=None,
                query=self.replace_field_with_lookup(self.document.db_entity_data.query, column_key, referred_table, referred_table_field)
            )
            return reference
        else:
            return super().handle_edit_key(key)

    def replace_field_with_lookup(self, query: DbQuery, column_key: str, referred_table: str, referred_table_field: str) -> DbQuery:
        return query.with_selectors(
            [s for s in self.document.table_selectors()]
        )
