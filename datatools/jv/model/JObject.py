from typing import Tuple, AnyStr, Optional

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JComplexElement import JComplexElement
from datatools.jv.model.JObjectEnd import JObjectEnd
from datatools.jv.model.JObjectStart import JObjectStart


class JObject(JComplexElement[dict]):

    def __init__(self, key: Optional[str] = None, indent=0, last_in_parent=True) -> None:
        super().__init__(None, key, indent, last_in_parent)
        self.start = JObjectStart(key, indent)
        self.start.parent = self
        self.end = JObjectEnd(None, indent, last_in_parent)
        self.end.parent = self

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '{…}', Highlighting.CURRENT.for_curly_braces()
