from typing import AnyStr, Tuple, List

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style


class JElement:
    indent: int
    has_trailing_comma: bool

    parent: 'JElement'
    line: int
    collapsed: bool

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        self.indent = indent
        self.has_trailing_comma = has_trailing_comma
        self.collapsed = False

    def __iter__(self): pass

    def layout(self, line: int) -> int:
        self.line = line
        return line + 1

    def rich_text(self) -> Tuple[AnyStr, Style]: pass

    def rich_text_length(self) -> int:
        return sum((len(span[0]) for span in self.spans()))

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        return [(' ' * self.indent, Style()), self.rich_text()] + self.rich_text_comma()

    def rich_text_comma(self) -> List[Tuple[AnyStr, Style]]:
        return [(',', Highlighting.CURRENT.for_comma())] if self.has_trailing_comma else []
