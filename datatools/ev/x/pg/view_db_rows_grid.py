import json
from typing import Any

from datatools.dbview.x.util.pg_query import query_to_string
from datatools.ev.x.pg.db_entity_data import DbEntityData
from datatools.json.util import to_jsonisable
from datatools.jt.app.ng import collapsed_columns
from datatools.jt.app.ng.jt_ng_grid import JtNgGrid
from datatools.tui.picotui_keys import *
from datatools.util.object_exporter import ObjectExporter


class ViewDbRowsGrid(JtNgGrid):
    db_entity_data: DbEntityData
    document: 'ViewDbRows'

    def handle_edit_key(self, key):
        if key == KEY_SHIFT_F5:
            # self.export_json_lines(0, self.data_bundle.orig_data, f'data from {self.db_entity_data.query.table}')
            self.export_json_lines2(self.data_bundle.orig_data, f'data from {self.db_entity_data.query.table}')
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
        elif key == KEY_CTRL_E:
            self.document.export_entity()
        elif key == KEY_CTRL_X:
            self.document.export_entity2()
        elif key == KEY_CTRL_R:
            column_key = self.column_keys[self.cursor_column]
            return self.document.resolved_column_entity_ref(column_key)
        else:
            return super().handle_edit_key(key)

    def export_json_lines2(self, content: list[Any], title: str | None = None):
        ObjectExporter.INSTANCE.export_multipart(
            {
                'X-Title': title,
                'Content-Type': 'application/json-lines',
                'Content': ''.join(json.dumps(to_jsonisable(row), ensure_ascii=False) + '\n' for row in content),
                'Collapsed-Columns': json.dumps(collapsed_columns(self.column_count, self.column_cell_renderer_f))
            }
        )
