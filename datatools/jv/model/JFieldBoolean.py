from typing import AnyStr, Tuple

from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model import JBoolean
from datatools.jv.model.JObjectFieldPrimitive import JObjectFieldPrimitive


class JFieldBoolean(JObjectFieldPrimitive):
    value: bool

    def __init__(self, value: bool, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.value = value

    def __repr__(self):
        return JBoolean.value_repr(self.value)

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return JBoolean.rich_text_for(self.value)
