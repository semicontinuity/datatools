from datatools.jt.app.ng.jt_ng_grid import JtNgGrid
from datatools.tui.picotui_keys import *
from datatools.util.object_exporter import ObjectExporter


class ViewDbRowsGrid(JtNgGrid):
    sql: str

    def handle_edit_key(self, key):
        if key == KEY_CTRL_ALT_SHIFT_F5:
            ObjectExporter.INSTANCE.export(
                self.sql,
                {"Content-Type": "application/sql"},
                0
            )

        else:
            return super().handle_edit_key(key)
