from datatools.jv.model.JElement import JElement


class JPrimitiveElement(JElement):
    def __iter__(self):
        yield self
