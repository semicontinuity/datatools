from typing import List

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
            width = max(width, len(str(element)))
            height += 1
            elements.append(element)

        self.width = width
        self.height = height
        self.elements = elements

    def row_to_string(self, y, x_from, x_to):
        if y < len(self.elements):
            s = str(self.elements[y])
            return s[x_from:x_to] + ' ' * (x_to - len(s))
        else:
            return ' ' * (x_to - x_from)
