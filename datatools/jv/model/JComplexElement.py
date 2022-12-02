from typing import List

from datatools.jv.model.JElement import JElement


class JComplexElement(JElement):
    start: JElement
    elements: List[JElement]
    end: JElement

    def __iter__(self):
        if self.collapsed:
            yield self
        else:
            yield self.start
            for field in self.elements:
                yield from field
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

    def optimize_layout(self, height):
        if self.size > height:
            for element in self.elements:
                element.collapsed = True
