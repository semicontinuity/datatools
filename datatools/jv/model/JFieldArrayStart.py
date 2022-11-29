from typing import Tuple, AnyStr, List

from datatools.json.json2ansi_toolkit import Style
from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.model.JObjectField import JObjectField
from datatools.jv.model.JElement import JElement


class JFieldArrayStart(JElement):
    name: str

    def __init__(self, name: str, indent=0) -> None:
        super().__init__(indent)
        self.name = name

    def __str__(self):
        return ' ' * self.indent + JObjectField.field_name_repr(self.name) + '['

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        return JObjectField.spans_for_field_name(self.indent, self.name) + [('{', Highlighting.CURRENT.for_curly_braces())]
