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

    def optimize_layout(self, height):
        # Size of primitive or collapsed element is 1
        # The excessive size is 'budget' to fill with expanded elements
        budget = height - 2 - len(self.elements)
        sorted_elements = sorted(self.elements, key=lambda e: e.size)
        for e in sorted_elements:
            # raise Exception(e)
            if e.size == 1:
                continue
            e.optimize_layout(height)
            if e.size - 1 > budget:  # 1 is already accounted for in len(self.elements)
                e.collapsed = True
            budget -= (e.size - 1)
