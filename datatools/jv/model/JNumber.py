from typing import Tuple, AnyStr, Optional

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JNumber(JPrimitiveElement):
    value: float

    def __init__(self, name: Optional[str], value: float, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.value = value

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return str(self.value), Highlighting.CURRENT.for_number()
