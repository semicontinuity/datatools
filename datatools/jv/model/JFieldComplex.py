from typing import List

from datatools.jv.model.JElement import JElement
from datatools.jv.model.JObjectField import JObjectField


class JFieldComplex(JObjectField):
    start: JElement
    elements: List[JElement]
    end: JElement

    def __iter__(self):
        if self.collapsed:
            yield self
        else:
            yield self.start
            for item in self.elements:
                yield from item
            yield self.end

    def layout(self, line: int) -> int:
        if self.collapsed:
            return super().layout(line)
        else:
            self.line = line
            line = self.start.layout(line)
            for item in self.elements:
                line = item.layout(line)
            line = self.end.layout(line)
            self.size = line - self.line
            return line

