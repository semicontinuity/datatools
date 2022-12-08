from typing import AnyStr, Tuple

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.jv.model.JSyntaxElement import JSyntaxElement


class JObjectStart(JSyntaxElement):

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '{', Highlighting.CURRENT.for_curly_braces()

