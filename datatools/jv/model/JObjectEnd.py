from typing import List, Tuple, AnyStr

from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model import JElement


class JObjectEnd(JElement):

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)

    def __repr__(self) -> str:
        return "}"

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '}', Highlighting.CURRENT.for_curly_braces()
