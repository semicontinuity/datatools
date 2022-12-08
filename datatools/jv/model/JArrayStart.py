from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.jv.model.JSyntaxElement import JSyntaxElement


class JArrayStart(JSyntaxElement):

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '[', Highlighting.CURRENT.for_square_brackets()
