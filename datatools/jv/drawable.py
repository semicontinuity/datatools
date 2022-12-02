from typing import List

from datatools.jv.highlighting.rich_text import render_substr
from datatools.jv.model import JElement


class Drawable:
    v: JElement

    width: int
    height: int
    elements: List[JElement]

    def __init__(self, v: JElement) -> None:
        self.v = v

    def layout(self):
        width = 0
        height = 0
        elements = []

        for element in self.v:
            width = max(width, element.rich_text_length())
            elements.append(element)
            height += 1

        self.v.layout(0)
        self.width = width
        self.height = height
        self.elements = elements

    def optimize_layout(self, height):
        self.v.optimize_layout(height)

    def row_to_string(self, y, x_from, x_to):
        if y < len(self.elements):
            return render_substr(self.elements[y].spans(), x_from, x_to)
        else:
            return ' ' * (x_to - x_from)

    def indent(self, y) -> int:
        if y < len(self.elements):
            return self.elements[y].indent

    def parent_of(self, line) -> JElement:
        element = self.elements[line]
        while True:
            if element.parent is None:
                return element
            elif element.parent.line != element.line:
                return element.parent
            else:
                element = element.parent

    def parent_line_of(self, line) -> int:
        return self.parent_of(line).line

    def collapse(self, line) -> int:
        parent = self.parent_of(line)
        parent.collapsed = True
        return parent.line

    def expand(self, line):
        self.elements[line].collapsed = False
