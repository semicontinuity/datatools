from typing import List

from datatools.jv.model.JFieldObjectEnd import JFieldObjectEnd
from datatools.jv.model.JFieldObjectStart import JFieldObjectStart
from datatools.jv.model.JObjectField import JObjectField


class JFieldObject(JObjectField):
    start: JFieldObjectStart
    fields: List[JObjectField]
    end: JFieldObjectEnd

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.start = JFieldObjectStart(name, indent)
        self.end = JFieldObjectEnd(indent, has_trailing_comma)

    def __iter__(self):
        yield self.start
        for field in self.fields:
            yield from field
        yield self.end
