from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting_holder import get_current_highlighting
from datatools.jv.model.JSyntaxElement import JSyntaxElement
from datatools.tui.treeview.rich_text import Style


class JArrayStart(JSyntaxElement):

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '[', get_current_highlighting().for_square_brackets()
