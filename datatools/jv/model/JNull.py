from types import NoneType
from typing import Tuple, AnyStr

from datatools.jv.highlighting.holder import get_current_highlighting
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement
from datatools.tui.rich_text import Style


class JNull(JPrimitiveElement[NoneType]):

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return "null", get_current_highlighting().for_null()
