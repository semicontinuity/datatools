from typing import Tuple, AnyStr

from datatools.misc.tree_table.jv import format_float
from datatools.misc.tree_table.jv.highlighting.highlighting import Highlighting
from datatools.misc.tree_table.jv.model.JPrimitiveElement import JPrimitiveElement
from datatools.tui.treeview.rich_text import Style


class JString(JPrimitiveElement[str]):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        s = format_float(self.value)
        return ''.join([JString.escape(c) for c in s]), Highlighting.CURRENT.for_number(False, self.indent)

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
