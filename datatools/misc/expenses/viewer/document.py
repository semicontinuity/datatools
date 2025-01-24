from datatools.tui.treeview.treedocument import TreeDocument


class JDocument(TreeDocument):

    def selected_value(self, line):
        return self.rows[line].get_value()

    def selected_path(self, line) -> str:
        if line == 0:
            return '.'

        path = []
        node = self.rows[line]

        while True:
            node = node.get_value_element()
            if node is self.root:
                return ''.join(reversed(path))

            path.append(node.get_selector())
            node = node.parent
