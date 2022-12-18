from datatools.jv.model.JElement import JElement


class JSyntaxElement(JElement):

    def set_collapsed_recursive(self, collapsed: bool):
        super(JSyntaxElement, self).set_collapsed_recursive(collapsed)
        if self.parent is not None:
            self.parent.set_collapsed_recursive(collapsed)

    def get_value(self):
        return self.parent.value

    def get_selector(self):
        return self.parent.get_selector()

    def get_value_element(self):
        return self.parent
