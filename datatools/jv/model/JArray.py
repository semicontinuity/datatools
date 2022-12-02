from typing import List, Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JArrayEnd import JArrayEnd
from datatools.jv.model.JArrayStart import JArrayStart
from datatools.jv.model.JElement import JElement


class JArray(JElement):
    """ Top-level array """
    start: JArrayStart
    items: List[JElement]
    end: JArrayEnd

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.start = JArrayStart(indent)
        self.end = JArrayEnd(indent, has_trailing_comma)

    def __iter__(self):
        if self.collapsed:
            yield self
        else:
            yield self.start
            for item in self.items:
                yield from item
            yield self.end

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '[…]', Highlighting.CURRENT.for_square_brackets()

    def layout(self, line: int) -> int:
        if self.collapsed:
            return super().layout(line)
        else:
            self.line = line
            line = self.start.layout(line)
            for item in self.items:
                line = item.layout(line)
            return self.end.layout(line)
