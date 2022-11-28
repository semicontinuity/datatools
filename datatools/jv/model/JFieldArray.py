from typing import List

from datatools.jv.model.JElement import JElement
from datatools.jv.model.JFieldArrayEnd import JFieldArrayEnd
from datatools.jv.model.JFieldArrayStart import JFieldArrayStart
from datatools.jv.model.JObjectField import JObjectField


class JFieldArray(JObjectField):
    start: JFieldArrayStart
    items: List[JElement]
    end: JFieldArrayEnd

    def __init__(self, name: str, items: List[JElement], indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.start = JFieldArrayStart(name, indent)
        self.items = items
        self.end = JFieldArrayEnd(indent, has_trailing_comma)

    def elements(self):
        yield self.start
        for field in self.items:
            yield from field.elements()
        yield self.end
