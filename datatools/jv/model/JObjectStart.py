from typing import AnyStr, Tuple

from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model import JElement


class JObjectStart(JElement):

    def __init__(self, indent=0) -> None:
        super().__init__(indent)

    def __repr__(self) -> str:
        return "{"

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '{', Highlighting.CURRENT.for_curly_braces()
