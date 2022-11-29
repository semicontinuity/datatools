from typing import Tuple, AnyStr

from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.JObjectFieldPrimitive import JObjectFieldPrimitive


class JFieldNumber(JObjectFieldPrimitive):
    value: str

    def __init__(self, value: str, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.value = value

    def __repr__(self):
        return JNumber.value_repr(self.value)

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return "null", Highlighting.CURRENT.for_null()
