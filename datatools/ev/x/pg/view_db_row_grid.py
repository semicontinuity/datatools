import json

from datatools.dbview.x.util.pg_query import query_to_string
from datatools.json.util import to_jsonisable
from datatools.jv.jgrid import JGrid
from datatools.tui.picotui_keys import KEY_CTRL_ALT_SHIFT_F5, KEY_SHIFT_F5, KEY_CTRL_E, KEY_CTRL_R, KEY_CTRL_Q, \
    KEY_CTRL_X
from datatools.util.object_exporter import ObjectExporter


class ViewDbRowGrid(JGrid):

    def handle_edit_key(self, key):
        if key == KEY_SHIFT_F5:
            ObjectExporter.INSTANCE.export(
                str(json.dumps(to_jsonisable(self.document.value))),
                {
                    "Content-Type": "application/json",
                    "X-Title": self.document.footer,
                },
                0
            )
        elif key == KEY_CTRL_ALT_SHIFT_F5:
            ObjectExporter.INSTANCE.export(
                query_to_string(self.document.query),
                {"Content-Type": "application/sql"},
                0
            )
        elif key == KEY_CTRL_Q:
            ObjectExporter.INSTANCE.export(
                query_to_string(self.document.query),
                {
                    "Content-Type": "application/sql",
                    "X-Title": self.document.footer,
                },
                0
            )
        elif key == KEY_CTRL_E:
            self.document.doc.export_entity()
        elif key == KEY_CTRL_X:
            self.document.doc.export_entity2()
        elif key == KEY_CTRL_R:
            path = self.document.selected_path(self.cur_line)
            if len(path) != 1:
                return
            return self.document.doc.resolved_column_entity_ref(path[0])
        else:
            return super().handle_edit_key(key)
