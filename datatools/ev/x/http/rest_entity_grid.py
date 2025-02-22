import json

from datatools.jv.jgrid import JGrid
from datatools.tui.picotui_keys import KEY_SHIFT_F5
from datatools.util.object_exporter import ObjectExporter


class RestEntityGrid(JGrid):

    def handle_edit_key(self, key):
        if key == KEY_SHIFT_F5:
            ObjectExporter.INSTANCE.export(
                json.dumps(self.document.value, ensure_ascii=False),
                {
                    "X-Title": self.document.footer,
                    "Content-Type": 'application/json',
                },
                0
            )
        else:
            return super().handle_edit_key(key)
