from typing import AnyStr, Tuple

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JSyntaxElement import JSyntaxElement


class JArrayEnd(JSyntaxElement):

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(None, indent, has_trailing_comma)

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return ']', Highlighting.CURRENT.for_square_brackets()
