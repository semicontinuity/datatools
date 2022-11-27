from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JBoolean(JPrimitiveElement):
    value: bool

    def __init__(self, value: bool, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.value = value

    def __repr__(self):
        return self.value_repr(self.value)

    @staticmethod
    def value_repr(value):
        return "true" if value else "false"
