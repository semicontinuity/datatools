from typing import Tuple, AnyStr, List

from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JElement import JElement


class JObjectField(JElement):
    """ Object's field (complete) """
    name: str

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.name = name

    @staticmethod
    def field_name_repr(name):
        return Highlighting.CURRENT.ansi_set_attrs_field_name() + f'"{name}"' + \
               Highlighting.CURRENT.ansi_set_attrs_field_colon() + ': '

    @staticmethod
    def spans_for_field_name(indent: int, name: str) -> List[Tuple[AnyStr, Style]]:
        """ Renders beginning of the string """
        return [
            (' ' * indent, Style()),
            (f'"{name}"', Highlighting.CURRENT.for_field_name()),
            (': ', Highlighting.CURRENT.for_colon())
        ]
