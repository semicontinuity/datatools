import json

from datatools.json.util import to_jsonisable
from datatools.jt.app.ng import collapsed_columns, filter_non_collapsed
from datatools.jt.model.exit_codes_mapping import KEYS_TO_EXIT_CODES
from datatools.jt.ui.ng.jt_ng_grid_base import JtNgGridBase
from datatools.tui.picotui_keys import *
from datatools.util.object_exporter import ObjectExporter


class JtNgGrid(JtNgGridBase):

    def handle_edit_key(self, key):
        def sort_value(row):
            value = row.get(self.column_keys[self.cursor_column])
            return '' if value is None else str(value)

        if key == KEY_CTRL_S:
            self.data_bundle.orig_data.sort(key=sort_value)
            self.redraw()
        elif key == KEY_F5 or key == KEY_ALT_F5:
            j = self.data_bundle.orig_data[self.cur_line]
            channel = key == KEY_ALT_F5
            self.export_json(channel, j)
        elif key == KEY_SHIFT_F5:
            j = self.data_bundle.orig_data
            channel = 0
            self.export_json_lines(channel, j)
        elif key == KEY_INSERT or key == KEY_ALT_INSERT:
            j = self.cell_value_f(self.cur_line, self.cursor_column)
            channel = key == KEY_ALT_INSERT
            self.export_json(channel, j)
        elif key == KEY_DELETE or key == KEY_ALT_DELETE:
            channel = key == KEY_ALT_DELETE
            j = {self.column_keys[self.cursor_column]: self.cell_value_f(self.cur_line, self.cursor_column)}
            self.export_json(channel, j)
        elif key in KEYS_TO_EXIT_CODES:
            return key
        else:
            return super().handle_edit_key(key)

    def export_json_lines(self, channel, j):
        collapsed = collapsed_columns(self.column_count, self.column_cell_renderer_f)
        j = [filter_non_collapsed(r, collapsed) for r in j]

        ObjectExporter.INSTANCE.export(
            ''.join(json.dumps(to_jsonisable(row), ensure_ascii=False) + '\n' for row in j),
            {'Content-Type': 'application/json-lines'},
            channel
        )

    def export_json(self, channel, j):
        ObjectExporter.INSTANCE.export(
            json.dumps(to_jsonisable(j), ensure_ascii=False),
            {'Content-Type': 'application/json'},
            channel
        )
