from typing import Tuple, AnyStr, Optional

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JArrayEnd import JArrayEnd
from datatools.jv.model.JArrayStart import JArrayStart
from datatools.jv.model.JComplexElement import JComplexElement


class JArray(JComplexElement):

    def __init__(self, name: Optional[str], indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.start = JArrayStart(name, indent)
        self.end = JArrayEnd(indent, has_trailing_comma)

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '[…]', Highlighting.CURRENT.for_square_brackets()
