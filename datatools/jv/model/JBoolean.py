from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JBoolean(JPrimitiveElement[bool]):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        return ("true", Highlighting.CURRENT.for_true()) \
            if self.value \
            else ("false", Highlighting.CURRENT.for_false())
