from typing import Tuple, AnyStr

from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JNull(JPrimitiveElement):

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)

    def __repr__(self):
        return "null"

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return "null", Highlighting.CURRENT.for_null()
