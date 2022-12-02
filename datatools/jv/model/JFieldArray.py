from typing import List, Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JFieldArrayEnd import JFieldArrayEnd
from datatools.jv.model.JFieldArrayStart import JFieldArrayStart
from datatools.jv.model.JFieldComplex import JFieldComplex
from datatools.jv.model.JObjectField import JObjectField


class JFieldArray(JFieldComplex):

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.start = JFieldArrayStart(name, indent)
        self.end = JFieldArrayEnd(indent, has_trailing_comma)

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        """ (Used only if in collapsed state) """
        return JObjectField.spans_for_field_name(self.indent, self.name) + [('[…]', Highlighting.CURRENT.for_square_brackets())]

