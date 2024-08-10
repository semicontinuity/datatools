from typing import AnyStr, Tuple

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.highlighting_holder import get_current_highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.jv.model.JSyntaxElement import JSyntaxElement


class JObjectStart(JSyntaxElement):

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '{', get_current_highlighting().for_curly_braces()

