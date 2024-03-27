from datatools.misc.tree_table.jv.highlighting.highlighting import Highlighting
from datatools.misc.tree_table.jv.model.JElement import JElement


class JFolderSummary(JElement):

    def style(self):
        return Highlighting.CURRENT.for_number(True, self.indent)

    def set_collapsed_recursive(self, collapsed: bool):
        super(JElement, self).set_collapsed_recursive(collapsed)
        if self.parent is not None:
            self.parent.set_collapsed_recursive(collapsed)

    def set_collapsed_children(self, collapsed: bool):
        super(JElement, self).set_collapsed_children(collapsed)
        if self.parent is not None:
            self.parent.set_collapsed_children(collapsed)

    def get_value(self):
        return self.parent.value

    def get_selector(self):
        return self.parent.get_selector()

    def get_value_element(self):
        return self.parent

    def get_padding(self): return self.parent.padding
