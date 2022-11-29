from typing import Tuple, AnyStr

from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.highlighting.rich_text import Style
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

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return str(self.value), Highlighting.CURRENT.for_number()
