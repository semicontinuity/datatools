from typing import Tuple, AnyStr

from datatools.misc.tree_table.jv.highlighting.highlighting import Highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.misc.tree_table.jv.model.JPrimitiveElement import JPrimitiveElement


class JString(JPrimitiveElement[str]):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        s = f'{self.value:g}'
        return ''.join([JString.escape(c) for c in s]), Highlighting.CURRENT.for_string()

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
