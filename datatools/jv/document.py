from datatools.tui.treeview.treedocument import TreeDocument


class JDocument(TreeDocument):

    def collapse(self, line) -> int:
        parent = self.rows[line].parent
        if parent is not None:
            parent.collapsed = True
            return parent.line
        else:
            return line

    def selected_value(self, line) -> int:
        return self.rows[line].get_value()
