from typing import AnyStr, Tuple, List, Optional

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style


class JElement:

    indent: int
    key: Optional[str]
    padding: int
    last_in_parent: bool

    parent: 'JElement'
    line: int
    size: int
    collapsed: bool

    def __init__(self, key: Optional[str] = None, indent=0, last_in_parent=True) -> None:
        self.key = key
        self.indent = indent
        self.last_in_parent = last_in_parent
        self.collapsed = False
        self.padding = 0

    def __iter__(self): pass

    def layout(self, line: int) -> int:
        self.line = line
        self.size = 1
        return line + 1

    def rich_text(self) -> Tuple[AnyStr, Style]: pass

    def rich_text_length(self) -> int:
        return sum((len(span[0]) for span in self.spans()))

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        return [(' ' * self.indent, Style())] + self.spans_for_field_label() + [self.rich_text()] + self.spans_for_comma()

    def spans_for_field_label(self) -> List[Tuple[AnyStr, Style]]:
        return [
            (f'"{self.key}"' + ' ' * self.padding, Highlighting.CURRENT.for_field_label(self.key)),
            (': ', Highlighting.CURRENT.for_colon()),
        ] if self.key is not None else []

    def spans_for_comma(self) -> List[Tuple[AnyStr, Style]]:
        return [] if self.last_in_parent else [(',', Highlighting.CURRENT.for_comma())]

    def optimize_layout(self, height): pass

    def set_collapsed_recursive(self, collapsed: bool):
        self.collapsed = collapsed
