from picotui.defs import KEY_F4

from datatools.jt.model.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.jt.ui.ng.grid import WGrid
from datatools.tui.picotui_keys import *
from datatools.util.object_exporter import ObjectExporter


class JtNgGrid(WGrid):

    def handle_edit_key(self, key):
        def sort_value(row):
            value = row.get(self.column_keys[self.cursor_column])
            return '' if value is None else str(value)

        if key == KEY_F4:
            self.data_bundle.orig_data.sort(key=sort_value)
            self.redraw()
        elif key == KEY_F5 or key == KEY_ALT_F5:
            ObjectExporter.INSTANCE.export(
                self.data_bundle.orig_data[self.cur_line],
                {},
                key == KEY_ALT_F5
            )
        elif key == KEY_INSERT or key == KEY_ALT_INSERT:
            ObjectExporter.INSTANCE.export(
                self.cell_value_f(self.cur_line, self.cursor_column),
                {},
                key == KEY_ALT_INSERT
            )
        elif key == KEY_DELETE or key == KEY_ALT_DELETE:
            ObjectExporter.INSTANCE.export(
                {self.column_keys[self.cursor_column]: self.cell_value_f(self.cur_line, self.cursor_column)},
                {},
                key == KEY_ALT_DELETE
            )
        elif key in KEYS_TO_EXIT_CODES:
            return key
        else:
            return super().handle_edit_key(key)
