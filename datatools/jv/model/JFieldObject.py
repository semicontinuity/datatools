from typing import List, Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JFieldComplex import JFieldComplex
from datatools.jv.model.JFieldObjectEnd import JFieldObjectEnd
from datatools.jv.model.JFieldObjectStart import JFieldObjectStart
from datatools.jv.model.JObjectField import JObjectField


class JFieldObject(JFieldComplex):

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.start = JFieldObjectStart(name, indent)
        self.end = JFieldObjectEnd(indent, has_trailing_comma)

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        """ (Used only if in collapsed state) """
        return JObjectField.spans_for_field_name(self.indent, self.name) + [('{…}', Highlighting.CURRENT.for_curly_braces())]
