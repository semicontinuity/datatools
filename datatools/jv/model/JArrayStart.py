from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JElement import JElement


class JArrayStart(JElement):

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '[', Highlighting.CURRENT.for_square_brackets()
