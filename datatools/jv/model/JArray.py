from typing import Tuple, AnyStr, Optional, Any, List

from datatools.jv.highlighting.holder import get_current_highlighting
from datatools.jv.model.JArrayEnd import JArrayEnd
from datatools.jv.model.JArrayStart import JArrayStart
from datatools.jv.model.JComplexElement import JComplexElement
from datatools.jv.model.JValueElement import JValueElement
from datatools.tui.treeview.rich_text import Style


class JArray(JComplexElement):

    def __init__(self, value: List[Any], key: Optional[str], elements: List[JValueElement]) -> None:
        super().__init__(value, key)
        self.start = JArrayStart(key)
        self.start.parent = self
        self.end = JArrayEnd(None)
        self.end.parent = self
        self.set_elements(elements)

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '[…]', get_current_highlighting().for_square_brackets()
