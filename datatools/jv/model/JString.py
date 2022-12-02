from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JString(JPrimitiveElement):
    value: str

    def __init__(self, name, value, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.value = value

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return JString.rich_text_for(self.value)

    @staticmethod
    def rich_text_for(value: AnyStr) -> Tuple[AnyStr, Style]:
        return '"' + ''.join([JString.escape(c) for c in value]) + '"', Highlighting.CURRENT.for_string()

    @staticmethod
    def escape(c: str):
        if c == '\b': return "\\b"
        if c == '\t': return "\\t"
        if c == '\n': return "\\n"
        if c == '\r': return "\\r"
        if c == '\\': return "\\\\"
        if c == '"': return "\\\""
        # Add unicode stuff?
        return c
