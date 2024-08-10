from types import NoneType
from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.highlighting_holder import get_current_highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JNull(JPrimitiveElement[NoneType]):

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return "null", get_current_highlighting().for_null()
