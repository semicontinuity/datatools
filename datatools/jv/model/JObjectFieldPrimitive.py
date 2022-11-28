from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.model.JObjectField import JObjectField


class JObjectFieldPrimitive(JObjectField):
    """ Object's field (complete) """

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)

    def __iter__(self):
        yield self

    def __str__(self):
        return ' ' * self.indent + \
               Highlighting.CURRENT.ansi_set_attrs_field_name() + f'"{self.name}"' +\
               Highlighting.CURRENT.ansi_set_attrs_field_colon() + ': ' + repr(self) +\
               (Highlighting.CURRENT.ansi_set_attrs_comma() + ',' if self.has_trailing_comma else '') +\
               Highlighting.CURRENT.ansi_reset_attrs()

