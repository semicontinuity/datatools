from typing import List

from datatools.jv.model.JElement import JElement
from datatools.jv.model.JObjectEnd import JObjectEnd
from datatools.jv.model.JObjectField import JObjectField
from datatools.jv.model.JObjectStart import JObjectStart


class JObject(JElement):
    """ Top-level object """
    start: JObjectStart
    fields: List[JObjectField]
    end: JObjectEnd

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.start = JObjectStart(indent)
        self.end = JObjectEnd(indent, has_trailing_comma)

    def __iter__(self):
        yield self.start
        for field in self.fields:
            yield from field
        yield self.end

    def layout(self, line: int):
        self.line = line

        line = self.start.layout(line)

        for item in self.fields:
            line = item.layout(line)

        return self.end.layout(line)
