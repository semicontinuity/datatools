from typing import List
from typing import TypeVar, Generic

from datatools.misc.tree_table.jv.model.JElement import JElement
from datatools.misc.tree_table.jv.model.JValueElement import JValueElement

V = TypeVar('V')


class JComplexElement(Generic[V], JValueElement[V]):
    start: JElement
    elements: List[JValueElement]

    def set_elements(self, elements: List[JValueElement]):
        self.elements = elements
        self.packed_size = 1 + len(elements)

    def sub_elements(self) -> List[JValueElement]:
        return self.elements

    def __iter__(self):
        if self.collapsed:
            yield self
        else:
            yield self.start
            for field in self.elements:
                yield from field

    def layout(self, line: int) -> int:
        if self.collapsed:
            return super().layout(line)
        else:
            self.line = line
            line = self.start.layout(line)
            for item in self.elements:
                line = item.layout(line)
            self.size = line - self.line
            return line

    def optimize_layout(self, height):
        self.set_expanded_recursive(self.optimal_depth_for(height))

    def optimal_depth_for(self, height):
        h = 0
        depth = 0
        while True:
            hh = self.compacted_size(depth)
            if hh > height * 1.5:
                depth -= 1
                break
            if hh == h:
                break
            depth += 1
            h = hh
        return depth

    def set_collapsed_children(self, collapsed: bool):
        super(JComplexElement, self).set_collapsed_children(collapsed)
        for element in self.elements:
            element.collapsed = collapsed

    def set_collapsed_recursive(self, collapsed: bool):
        super(JComplexElement, self).set_collapsed_recursive(collapsed)
        for element in self.elements:
            element.set_collapsed_recursive(collapsed)

    def set_expanded_recursive(self, depth: int):
        if depth == 0:
            super(JComplexElement, self).set_collapsed_recursive(True)
            return

        super(JComplexElement, self).set_collapsed_recursive(False)
        for element in self.elements:
            element.set_expanded_recursive(depth - 1)

    def show_plus(self):
        return self.collapsed

    def is_folder(self):
        return True

    def compacted_size(self, depth: int):
        if depth == 0:
            return 1
        else:
            return 1 + sum(e.compacted_size(depth - 1) for e in self.elements)
