from typing import Tuple, AnyStr

from datatools.json.util import escape
from datatools.jv.highlighting.holder import get_current_highlighting
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement
from datatools.tui.treeview.rich_text import Style


class JString(JPrimitiveElement[str]):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        escaped = ''.join([escape(c) for c in self.value])
        if escaped != self.value or self.options.quotes:
            return '"' + escaped + '"', self.value_style()
        else:
            return self.value, self.value_style()

    def value_style(self) -> Style:
        return get_current_highlighting().for_string(self)
