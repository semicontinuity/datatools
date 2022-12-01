from typing import List

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
        yield self.start
        for item in self.items:
            yield from item.__iter__()
        yield self.end

    def layout(self, line: int) -> int:
        self.line = line

        line = self.start.layout(line)

        for item in self.items:
            line = item.layout(line)

        return self.end.layout(line)
