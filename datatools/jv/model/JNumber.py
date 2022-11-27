from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JNumber(JPrimitiveElement):
    value: float

    def __init__(self, value: float):
        self.value = value

    def __repr__(self):
        return str(self.value)
