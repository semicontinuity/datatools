import json

from datatools.dbview.x.util.db_query import DbQuery
from datatools.json.util import to_jsonisable
from datatools.jt.app.ng.jt_ng_grid import JtNgGrid
from datatools.tui.picotui_keys import *
from datatools.util.object_exporter import ObjectExporter


class ViewDbRowsGrid(JtNgGrid):
    sql: str
    query: DbQuery

    def handle_edit_key(self, key):
        if key == KEY_CTRL_ALT_SHIFT_F5:
            ObjectExporter.INSTANCE.export(
                self.sql,
                {"Content-Type": "application/sql"},
                0
            )
        elif key == KEY_CTRL_Q:
            ObjectExporter.INSTANCE.export(
                json.dumps(to_jsonisable(self.query)),
                {"Content-Type": "application/json"},
                0
            )
        elif key == KEY_CTRL_R:
            # self.cursor_column
            return
        else:
            return super().handle_edit_key(key)
