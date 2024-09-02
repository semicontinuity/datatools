from typing import Tuple, AnyStr

from datatools.jv.highlighting.holder import get_current_highlighting
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement
from datatools.tui.treeview.rich_text import Style


class JString(JPrimitiveElement[str]):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '"' + ''.join([JString.escape(c) for c in self.value]) + '"', self.value_style()

    def value_style(self):
        return get_current_highlighting().for_string(self)

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
