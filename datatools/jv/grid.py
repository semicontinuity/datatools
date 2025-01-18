from datatools.tui.picotui_keys import KEY_INSERT
from datatools.tui.treeview.grid import WGrid
from datatools.tui.treeview.treedocument import TreeDocument
from datatools.util.object_exporter import ObjectExporter


class JGrid(WGrid):
    search_str: str

    def __init__(self, x: int, y: int, width, height, document: TreeDocument, interactive=True):
        super().__init__(x, y, width, height, document, interactive)
        self.search_str = ""

    def handle_cursor_keys(self, key):
        self.search_str = ""
        return super().handle_cursor_keys(key)

    def handle_edit_key(self, key):
        if key == KEY_INSERT:
            ObjectExporter.INSTANCE.export(
                self.document.selected_value(self.cur_line),
                {"title": self.document.selected_path(self.cur_line)},
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
        # line = self.search()
        # if line is not None:
        #     content_height = self.height - 3
        #     if line >= self.top_line + content_height:
        #         delta = line - self.cur_line
        #         self.top_line += delta
        #     self.cur_line = line
        #     self.redraw_lines(self.top_line, content_height)
