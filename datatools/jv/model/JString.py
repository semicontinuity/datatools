from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.highlighting_holder import get_current_highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JString(JPrimitiveElement[str]):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '"' + ''.join([JString.escape(c) for c in self.value]) + '"', get_current_highlighting().for_string()

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
