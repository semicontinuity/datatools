import json

from datatools.dbview.x.util.pg_query import query_to_string
from datatools.json.util import to_jsonisable
from datatools.jv.jgrid import JGrid
from datatools.tui.picotui_keys import KEY_CTRL_ALT_SHIFT_F5, KEY_SHIFT_F5, KEY_CTRL_E
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
                {
                    "Content-Type": "application/sql",
                    "X-Title": self.document.footer,
                },
                0
            )
        elif key == KEY_CTRL_E:
            ObjectExporter.INSTANCE.export(
                str(
                    json.dumps(
                        to_jsonisable(
                            self.document.query,
                        )
                    )
                ),
                {
                    "Content-Type": "application/x-basic-entity",
                    "X-Title": self.document.footer,
                    "X-Realm-Ctx": self.document.db_entity_data.realm_ctx,
                    "X-Realm-Ctx-Dir": self.document.db_entity_data.realm_ctx_dir,
                    "X-Entity-Realm-Path": self.document.db_entity_data.entity_realm_path,
                },
                0
            )
        else:
            return super().handle_edit_key(key)

