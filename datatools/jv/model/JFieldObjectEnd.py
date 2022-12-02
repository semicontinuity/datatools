from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JElement import JElement


class JFieldObjectEnd(JElement):

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(None, indent, has_trailing_comma)

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '}', Highlighting.CURRENT.for_curly_braces()
