from typing import Hashable, List, Optional, Any

from datatools.tui.treeview.tree_document import TreeDocument


class JDocument(TreeDocument):
    value: Any

    def collapse(self, line) -> int:
        parent = self.rows[line].parent
        if parent is not None:
            parent.collapsed = True
            return parent.line
        else:
            return line

    def selected_value_node(self, line):
        return self.rows[line].get_value_element()

    def selected_value(self, line):
        return self.rows[line].get_value()

    def selected_json_path(self, line) -> str:
        if line == 0:
            return '.'
        path = self.selected_path(line)
        return ''.join([f'[{k}]' if type(k) is int else f'.{k}' for k in path])

    def selected_path(self, line) -> List[Hashable]:
        return self.rows[line].path()

    def search(self, search_str: str, from_line: int) -> Optional[int]:
        for i in range(from_line, len(self.rows)):
            if search_str in self.rows[i]:
                return i
        for i in range(0, from_line):
            if search_str in self.rows[i]:
                return i
