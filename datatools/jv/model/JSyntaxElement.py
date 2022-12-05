from datatools.jv.model.JElement import JElement


class JSyntaxElement(JElement):

    def expand_recursive(self):
        super(JSyntaxElement, self).expand_recursive()
        if self.parent is not None:
            self.parent.expand_recursive()
