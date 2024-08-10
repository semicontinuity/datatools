from datatools.jv.model.JElement import JElement


class JSyntaxElement(JElement):

    def set_collapsed_recursive(self, collapsed: bool):
        super(JSyntaxElement, self).set_collapsed_recursive(collapsed)
        if self.parent is not None:
            self.parent.set_collapsed_recursive(collapsed)

    def set_collapsed_children(self, collapsed: bool):
        super(JSyntaxElement, self).set_collapsed_children(collapsed)
        if self.parent is not None:
            self.parent.set_collapsed_children(collapsed)

    def get_value(self):
        return self.parent.value

    def get_value_element(self):
        return self.parent

    def get_padding(self): return self.parent.padding
