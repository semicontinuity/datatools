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
            fields = self.document.referred_table_fields(self.column_keys[self.cursor_column])
            if fields is None:
                return

            field = choose(fields, f'Choose a field from {self.document.query.table}')
            if field is None:
                return

            reference = DbRowReference(
                realm_name=self.document.realm.name,
                selector=None,
                query=self.replace_field_with_lookup(self.document.db_entity_data.query)
            )
            return reference
        else:
            return super().handle_edit_key(key)

    def replace_field_with_lookup(self, query: DbQuery) -> DbQuery:
        return query.with_selectors(self.document.table_selectors())
