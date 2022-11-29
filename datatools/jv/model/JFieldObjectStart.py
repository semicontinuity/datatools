from typing import List, Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JObjectField import JObjectField


class JFieldObjectStart(JElement):
    name: str

    def __init__(self, name: str, indent=0) -> None:
        super().__init__(indent)
        self.name = name

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        return JObjectField.spans_for_field_name(self.indent, self.name) + [('{', Highlighting.CURRENT.for_curly_braces())]
