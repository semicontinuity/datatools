from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JNumber(JPrimitiveElement):
    value: float

    def __init__(self, value: float, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.value = value

    def __repr__(self):
        return JNumber.value_repr(self.value)

    @staticmethod
    def value_repr(value):
        return Highlighting.CURRENT.ansi_set_attrs_number() + str(value)
