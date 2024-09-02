from typing import List
from typing import TypeVar, Generic

from datatools.jv.model.JElement import JElement
from datatools.jv.model.JValueElement import JValueElement

V = TypeVar('V')


class JComplexElement(Generic[V], JValueElement[V]):
    start: JElement
    elements: List[JValueElement]
    end: JElement

    def set_elements(self, elements: List[JValueElement]):
        self.elements = elements
        self.packed_size = 1 + len(elements) + 1
        for e in elements:
            e.parent = self

    def sub_elements(self) -> List[JValueElement]:
        return self.elements

    def __iter__(self):
        if self.collapsed:
            yield self
        else:
            yield self.start
            for e in self.elements:
                yield from e
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
        # Initially, assume, that this element will be populated with only collapsed sub-elements
        budget = height - self.packed_size
        candidates = list(self.elements)
        next_candidates = []

        while True:
            for e in sorted(candidates, key=lambda e: e.packed_size):
                # Let's see if packed e fits into the budget (return 1 for collapsed element height back to the budget)
                if budget <= 0:
                    break

                if e.packed_size < budget + 1:
                    e.collapsed = False
                    budget -= (e.packed_size - 1)

                    for ee in e.sub_elements():
                        ee.collapsed = True
                        next_candidates.append(ee)
                else:
                    e.collapsed = True

            if budget <= 0 or len(next_candidates) == 0:
                break
            candidates = next_candidates
            next_candidates = []

        for e in next_candidates:
            if e.size > 1:
                e.optimize_layout(height)

    def set_collapsed_children(self, collapsed: bool):
        super(JComplexElement, self).set_collapsed_children(collapsed)
        for element in self.elements:
            element.collapsed = collapsed

    def set_collapsed_recursive(self, collapsed: bool):
        super(JComplexElement, self).set_collapsed_recursive(collapsed)
        for element in self.elements:
            element.set_collapsed_recursive(collapsed)

    def set_key(self, key: str):
        self.key = key
        self.start.key = key

    def set_last_in_parent(self, last_in_parent: bool):
        self.end.last_in_parent = last_in_parent
