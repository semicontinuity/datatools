from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JBoolean(JPrimitiveElement):
    value: bool

    def __init__(self, value: bool, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.value = value

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return JBoolean.rich_text_for(self.value)

    @staticmethod
    def rich_text_for(value: bool) -> Tuple[AnyStr, Style]:
        return ("true", Highlighting.CURRENT.for_true()) \
            if value \
            else ("false", Highlighting.CURRENT.for_false())
