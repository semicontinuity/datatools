from datatools.jv.model.JElement import JElement


class JPrimitiveElement(JElement):
    def elements(self):
        yield self
