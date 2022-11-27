from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JBoolean(JPrimitiveElement):
    value: bool

    def __init__(self, value: bool):
        self.value = value

    def __repr__(self):
        return "true" if self.value else "false"
