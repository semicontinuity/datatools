from typing import AnyStr, Tuple

from datatools.jv.highlighting.holder import get_current_highlighting
from datatools.jv.model.JSyntaxElement import JSyntaxElement
from datatools.tui.treeview.rich_text import Style


class JArrayEnd(JSyntaxElement):

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return ']', get_current_highlighting().for_square_brackets()
