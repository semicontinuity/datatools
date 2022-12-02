from typing import Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JNull(JPrimitiveElement):

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return "null", Highlighting.CURRENT.for_null()
