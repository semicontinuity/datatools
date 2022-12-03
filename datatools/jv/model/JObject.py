from typing import Tuple, AnyStr, Optional

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JComplexElement import JComplexElement
from datatools.jv.model.JObjectEnd import JObjectEnd
from datatools.jv.model.JObjectStart import JObjectStart


class JObject(JComplexElement[dict]):

    def __init__(self, name: Optional[str], indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, None, indent, has_trailing_comma)
        self.start = JObjectStart(name, indent)
        self.start.parent = self
        self.end = JObjectEnd(indent, has_trailing_comma)
        self.end.parent = self

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '{…}', Highlighting.CURRENT.for_curly_braces()
