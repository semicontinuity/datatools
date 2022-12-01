from typing import List

from datatools.jv.highlighting.rich_text import render_substr
from datatools.jv.model import JElement


class Drawable:
    width: int
    height: int
    elements: List[JElement]

    def __init__(self, v: JElement) -> None:
        width = 0
        height = 0
        elements = []

        for element in v:
            width = max(width, element.rich_text_length())
            elements.append(element)
            height += 1

        v.layout(0)

        self.width = width
        self.height = height
        self.elements = elements

    def row_to_string(self, y, x_from, x_to):
        if y < len(self.elements):
            return render_substr(self.elements[y].spans(), x_from, x_to)
        else:
            return ' ' * (x_to - x_from)

    def indent(self, y) -> int:
        if y < len(self.elements):
            return self.elements[y].indent

    def parent_line_of(self, line) -> int:
        element = self.elements[line]
        while True:
            if element.parent is None:
                return 0
            elif element.parent.line != element.line:
                return element.parent.line
            else:
                element = element.parent
