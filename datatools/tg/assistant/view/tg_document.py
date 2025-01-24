from time import sleep

from datatools.tui.treeview.treedocument import TreeDocument


class TgDocument(TreeDocument):

    # @override
    def collapse(self, line) -> int:
        element = self.rows[line]
        parent = element.parent

        if element is None:
            return line

        if element.collapsed:
            if parent is not None:
                parent.collapsed = True
                return parent.line
            else:
                return element.line
        else:
            element.collapsed = True
            return element.line
