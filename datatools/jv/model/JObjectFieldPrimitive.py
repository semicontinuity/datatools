from typing import Tuple, AnyStr, List

from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JObjectField import JObjectField


class JObjectFieldPrimitive(JObjectField):

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)

    def __iter__(self):
        yield self

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        return JObjectField.spans_for_field_name(self.indent, self.name) + [self.rich_text()] + self.spans_for_comma()
