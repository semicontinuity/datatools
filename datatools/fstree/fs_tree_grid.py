from typing import Optional

from picotui.defs import KEY_ESC, KEY_DELETE, KEY_BACKSPACE

from datatools.tui.picotui_keys import KEY_ALT_INSERT, KEY_ALT_DELETE
from datatools.tui.treeview.grid import WGrid
from datatools.tui.treeview.treedocument import TreeDocument


class FsTreeGrid(WGrid):
    search_str: Optional[str]

    def __init__(self, x: int, y: int, width, height, document: TreeDocument, interactive=True):
        super().__init__(x, y, width, height, document, interactive)
        self.search_str = None

    def before_redraw(self):
        pass

    def after_redraw(self):
        pass

    def handle_edit_key(self, key):
        if key == KEY_DELETE:
            node = self.document.get_node(self.cur_line)
            node.delete()
            self.document.refresh()
            if self.document.root.is_empty():
                return KEY_ESC
        elif key == KEY_ALT_INSERT:
            node = self.document.get_node(self.cur_line)
            node.mark()
            self.document.refresh()
        elif key == KEY_ALT_DELETE:
            node = self.document.get_node(self.cur_line)
            node.unmark()
            self.document.refresh()
        elif key == KEY_BACKSPACE:
            self.search_str = None
        else:
            result = super().handle_edit_key(key)
            if result:
                return result
            if type(key) is bytes:
                char = key.decode("utf-8")
                if char is not None:
                    self.handle_typed_char(char)

    def handle_typed_char(self, char):
        if self.search_str is None:
            self.search_str = ""
        self.search_str += char
        self.ensure_visible(self.search())

    def search(self) -> Optional[int]:
        line = self.cur_line
        while line < self.total_lines:
            s = self.document.get_node(line).name
            if s.find(self.search_str) >= 0:
                return line
            line += 1
        return None
