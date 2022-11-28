from typing import List

from datatools.jv.model.JArrayEnd import JArrayEnd
from datatools.jv.model.JArrayStart import JArrayStart
from datatools.jv.model.JElement import JElement


class JArray(JElement):
    """ Top-level array """
    start: JArrayStart
    items: List[JElement]
    end: JArrayEnd

    def __init__(self, items: List[JElement], indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.start = JArrayStart(indent)
        self.items = items
        self.end = JArrayEnd(indent, has_trailing_comma)

    def elements(self):
        yield self.start
        for item in self.items:
            yield from item.elements()
        yield self.end

