from datatools.jv.model.JElement import JElement


class JSyntaxElement(JElement):

    def set_collapsed_recursive(self, collapsed: bool):
        super(JSyntaxElement, self).set_collapsed_recursive(collapsed)
        if self.parent is not None:
            self.parent.set_collapsed_recursive(collapsed)
