from typing import AnyStr, Tuple, List

from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.highlighting.rich_text import Style


class JElement:
    indent: int
    has_trailing_comma: bool

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        self.indent = indent
        self.has_trailing_comma = has_trailing_comma

    def __iter__(self): pass

    def rich_text(self) -> Tuple[AnyStr, Style]: pass

    def __str__(self):
        return ' ' * self.indent + repr(self) + \
               (Highlighting.CURRENT.ansi_set_attrs_comma() + ',' if self.has_trailing_comma else '') + \
               Highlighting.CURRENT.ansi_reset_attrs()

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        return [(' ' * self.indent, Style()), self.rich_text()] + self.rich_text_comma()

    def rich_text_comma(self) -> List[Tuple[AnyStr, Style]]:
        return [(',', Highlighting.CURRENT.for_comma())] if self.has_trailing_comma else []
