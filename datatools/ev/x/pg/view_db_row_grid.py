import json

from datatools.json.util import to_jsonisable
from datatools.jv.jgrid import JGrid
from datatools.tui.picotui_keys import KEY_CTRL_ALT_SHIFT_F5
from datatools.util.object_exporter import ObjectExporter


class ViewDbRowGrid(JGrid):

    def handle_edit_key(self, key):
        if key == KEY_CTRL_ALT_SHIFT_F5:
            s = str(json.dumps(to_jsonisable(self.document.query)))
            ObjectExporter.INSTANCE.export(
                s,
                {
                    "Content-Type": "application/json",
                    "X-Title": self.document.footer,
                },
                0
            )
        else:
            return super().handle_edit_key(key)

