from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JComplexElement import JComplexElement
from datatools.jv.model.JObjectEnd import JObjectEnd
from datatools.jv.model.JObjectStart import JObjectStart


class JObject(JComplexElement):
    """ Top-level object """

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.start = JObjectStart(indent)
        self.end = JObjectEnd(indent, has_trailing_comma)

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '{…}', Highlighting.CURRENT.for_curly_braces()
