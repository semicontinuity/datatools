import json
import sys

from datatools.tui.picotui_keys import KEY_INSERT
from datatools.tui.treeview.grid import WGrid


class JGrid(WGrid):

    def handle_edit_key(self, key):
        if key == KEY_INSERT and not sys.stdout.isatty():
            print(json.dumps(self.document.selected_value(self.cur_line)))
            sys.stdout.flush()
        else:
            return super().handle_edit_key(key)
