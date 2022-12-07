from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JSyntaxElement import JSyntaxElement


class JObjectEnd(JSyntaxElement):

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '}', Highlighting.CURRENT.for_curly_braces()
