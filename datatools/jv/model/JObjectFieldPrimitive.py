from typing import Tuple, AnyStr, List

from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JObjectField import JObjectField


class JObjectFieldPrimitive(JObjectField):

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)

    def __iter__(self):
        yield self

    def __str__(self):
        return ' ' * self.indent + \
               JObjectField.field_name_repr(self.name) + \
               repr(self) + \
               (Highlighting.CURRENT.ansi_set_attrs_comma() + ',' if self.has_trailing_comma else '') + \
               Highlighting.CURRENT.ansi_reset_attrs()

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        return JObjectField.spans_for_field_name(self.indent, self.name) + [self.rich_text()] + self.rich_text_comma()
