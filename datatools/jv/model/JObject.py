from typing import Tuple, AnyStr, Optional, Dict, Any, Hashable, List

from datatools.jv.highlighting.holder import get_current_highlighting
from datatools.jv.model.JComplexElement import JComplexElement
from datatools.jv.model.JObjectEnd import JObjectEnd
from datatools.jv.model.JObjectStart import JObjectStart
from datatools.jv.model.JValueElement import JValueElement
from datatools.tui.treeview.rich_text import Style


class JObject(JComplexElement[dict]):

    def __init__(self, value: Dict[str, Any], key: Optional[Hashable], elements: List[JValueElement], indent=0, last_in_parent=True) -> None:
        super().__init__(value, key, indent, last_in_parent)
        self.start = JObjectStart(key, indent)
        self.start.parent = self
        self.end = JObjectEnd(None, indent, last_in_parent)
        self.end.parent = self
        self.set_elements(elements)

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '{…}', get_current_highlighting().for_curly_braces()
