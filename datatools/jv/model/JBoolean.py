from typing import Tuple, AnyStr

from datatools.jv.highlighting.holder import get_current_highlighting
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement
from datatools.tui.treeview.rich_text import Style


class JBoolean(JPrimitiveElement[bool]):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        return ("true", get_current_highlighting().for_true()) \
            if self.value \
            else ("false", get_current_highlighting().for_false())
