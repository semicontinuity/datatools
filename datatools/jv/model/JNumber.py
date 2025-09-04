from typing import Tuple, AnyStr

from datatools.jv.highlighting.holder import get_current_highlighting
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement
from datatools.tui.rich_text import Style


class JNumber(JPrimitiveElement[float]):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        return str(self.value), self.value_style()

    def value_style(self):
        return get_current_highlighting().for_number()
