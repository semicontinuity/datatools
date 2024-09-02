from typing import Hashable, List

from datatools.tui.treeview.treedocument import TreeDocument


class JDocument(TreeDocument):

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
