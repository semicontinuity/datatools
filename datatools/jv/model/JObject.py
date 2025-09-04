from typing import Tuple, AnyStr, Optional, Dict, Any, Hashable

from datatools.jv.highlighting.holder import get_current_highlighting
from datatools.jv.model.JComplexElement import JComplexElement
from datatools.jv.model.JObjectEnd import JObjectEnd
from datatools.jv.model.JObjectStart import JObjectStart
from datatools.tui.rich_text import Style


class JObject(JComplexElement[dict]):

    def __init__(self, value: Dict[str, Any], key: Optional[Hashable]) -> None:
        super().__init__(value, key)
        self.start = JObjectStart(key)
        self.start.parent = self
        self.end = JObjectEnd(None)
        self.end.parent = self

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '{…}', get_current_highlighting().for_curly_braces()
