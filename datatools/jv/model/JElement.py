from typing import AnyStr, Tuple, List, Optional

from datatools.json.coloring import hash_to_rgb_dark
from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.coloring import hash_to_rgb, hash_code


class JElement:
    key: Optional[str]

    indent: int
    has_trailing_comma: bool

    parent: 'JElement'
    line: int
    size: int
    collapsed: bool

    def __init__(self, name: Optional[str] = None, indent=0, has_trailing_comma=False) -> None:
        self.key = name
        self.indent = indent
        self.has_trailing_comma = has_trailing_comma
        self.collapsed = False

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
            (f'"{self.key}"', Highlighting.CURRENT.for_field_label(self.key)),
            (': ', Highlighting.CURRENT.for_colon())
        ] if self.key is not None else []

    def spans_for_comma(self) -> List[Tuple[AnyStr, Style]]:
        return [(',', Highlighting.CURRENT.for_comma())] if self.has_trailing_comma else []

    def optimize_layout(self, height): pass
