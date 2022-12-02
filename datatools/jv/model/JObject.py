from typing import List, Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JObjectEnd import JObjectEnd
from datatools.jv.model.JObjectField import JObjectField
from datatools.jv.model.JObjectStart import JObjectStart


class JObject(JElement):
    """ Top-level object """
    start: JObjectStart
    fields: List[JObjectField]
    end: JObjectEnd
    collapsed: bool

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.start = JObjectStart(indent)
        self.end = JObjectEnd(indent, has_trailing_comma)
        self.collapsed = False

    def __iter__(self):
        if self.collapsed:
            yield self
        else:
            yield self.start
            for field in self.fields:
                yield from field
            yield self.end

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '{…}', Highlighting.CURRENT.for_curly_braces()

    def layout(self, line: int) -> int:
        if self.collapsed:
            return super().layout(line)
        else:
            self.line = line
            line = self.start.layout(line)
            for item in self.fields:
                line = item.layout(line)
            return self.end.layout(line)
