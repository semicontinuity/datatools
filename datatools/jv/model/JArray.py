from typing import Tuple, AnyStr, Optional

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.jv.model.JArrayEnd import JArrayEnd
from datatools.jv.model.JArrayStart import JArrayStart
from datatools.jv.model.JComplexElement import JComplexElement


class JArray(JComplexElement):

    def __init__(self, key: Optional[str], indent=0, last_in_parent=True) -> None:
        super().__init__(None, key, indent, last_in_parent)
        self.start = JArrayStart(key, indent=indent)
        self.start.parent = self
        self.end = JArrayEnd(None, indent=indent, last_in_parent=last_in_parent)
        self.end.parent = self

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '[…]', Highlighting.CURRENT.for_square_brackets()
