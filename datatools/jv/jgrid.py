import json
from typing import Optional

from datatools.json.util import to_jsonisable
from datatools.tui.picotui_keys import KEY_INSERT, KEY_SHIFT_F5
from datatools.tui.treeview.tree_document import TreeDocument
from datatools.tui.treeview.tree_grid import TreeGrid
from datatools.util.object_exporter import ObjectExporter


class JGrid(TreeGrid):
    search_str: str

    def __init__(self, x: int, y: int, width, height, document: TreeDocument, interactive=True):
        super().__init__(x, y, width, height, document, interactive)
        self.search_str = ""

    def handle_cursor_keys(self, key):
        result = super().handle_cursor_keys(key)
        if result is not None:
            self.search_str = ""
            return result

    def handle_edit_key(self, key):
        if key == KEY_INSERT:
            value = self.document.selected_value(self.cur_line)
            selected_path = '/'.join(str(p) for p in self.document.selected_path(self.cur_line))
            if type(value) is str:
                ObjectExporter.INSTANCE.export(
                    value,
                    {
                        "X-Title": selected_path,
                        "Content-Type": 'text/plain',
                    },
                    0
                )
            else:
                ObjectExporter.INSTANCE.export(
                    json.dumps(to_jsonisable(value), ensure_ascii=False),
                    {
                        "X-Title": selected_path,
                        "Content-Type": 'application/json',
                    },
                    0
                )

        elif key == KEY_SHIFT_F5:
            ObjectExporter.INSTANCE.export(
                json.dumps(self.document.value, ensure_ascii=False),
                {
                    "X-Title": 'json',
                    "Content-Type": 'application/json',
                },
                0
            )
        else:
            node = self.document.selected_value_node(self.cur_line)
            result = node.handle_key(key)
            if result is not None:
                return result
            else:
                result = super().handle_edit_key(key)
                if result:
                    return result
                if type(key) is bytes:
                    self.handle_typed_key(key)

    def handle_typed_key(self, key):
        self.search_str += key.decode("utf-8")
        line = self.search()
        if line is not None:
            content_height = self.height
            if line >= self.top_line + content_height:
                delta = line - self.cur_line
                self.top_line += delta
            self.cur_line = line
            self.redraw_lines(self.top_line, content_height)

    def search(self) -> Optional[int]:
        if self.search_str == "":
            return None
        return self.document.search(self.search_str, self.cur_line)
