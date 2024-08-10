from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.holder import get_current_highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JNumber(JPrimitiveElement[float]):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        return str(self.value), get_current_highlighting().for_number()
