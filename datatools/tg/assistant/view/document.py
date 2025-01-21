from datatools.tui.treeview.treedocument import TreeDocument


class TgDocument(TreeDocument):

    # @override
    def collapse(self, line) -> int:
        element = self.rows[line]
        parent = element.parent
        if parent is not None:
            parent.collapsed = True
            return parent.line
        elif element is not None:
            element.collapsed = True
            return element.line
        else:
            return line
