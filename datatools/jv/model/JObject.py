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

    def __init__(self, fields: List[JObjectField], indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.start = JObjectStart(indent)
        self.fields = fields
        self.end = JObjectEnd(indent, has_trailing_comma)

    def elements(self):
        yield self.start
        for field in self.fields:
            yield from field.elements()
        yield self.end

