import json
import os
from typing import Optional

from datatools.json.util import to_jsonisable
from datatools.tui.picotui_keys import KEY_INSERT, KEY_SHIFT_F5
from datatools.tui.treeview.tree_document import TreeDocument
from datatools.tui.treeview.tree_grid import TreeGrid
from datatools.tui.tui_fd import infer_fd_tui
from datatools.util.object_exporter import ObjectExporter


class JGrid(TreeGrid):
    search_str: str

    def __init__(self, x: int, y: int, width, height, document: TreeDocument, interactive=True):
        super().__init__(x, y, width, height, document, interactive)
        self.search_str = ""
        self._terminal_size = None

    def handle_resize(self):
        super().handle_resize()
        if not self.interactive:
            return
        try:
            width, height = os.get_terminal_size(infer_fd_tui())
        except OSError:
            return
        if width <= 0 or height <= 0 or (width, height) == self._terminal_size:
            return
        self._terminal_size = width, height

        self.width = max(1, width - self.x)
        available_height = max(1, height - self.y)
        # Keep one content row even when the terminal cannot also fit the footer.
        self.y_bottom_offset = int(bool(self.document.footer) and available_height > 1)
        self.dynamic_helper.screen_height = height
        self.set_height(min(available_height, self.total_lines + self.y_bottom_offset))
        self.top_line = max(0, min(self.top_line, self.total_lines - self.rows_view_height))
        self.top_line = max(0, min(self.top_line, self.cur_line))
        if self.cur_line >= self.top_line + self.rows_view_height:
            self.top_line = self.cur_line - self.rows_view_height + 1
        self.x_shift = max(0, min(self.x_shift, self.document.width - self.width))

        self.attr_reset()
        self.clear_box(self.x, self.y, self.width, available_height)
        self.redraw()

    def redraw_footer(self):
        if self.y_bottom_offset:
            super().redraw_footer()

    def cell_cursor_place(self):
        if self.interactive and 0 <= self.cur_line < self.total_lines:
            cursor_x = self.document.rows[self.cur_line].indent - self.x_shift
            cursor_y = self.cur_line - self.top_line
            if 0 <= cursor_x < self.width and 0 <= cursor_y < self.rows_view_height:
                self.goto(self.x + cursor_x, self.y + cursor_y)
                self.cursor(True)

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
