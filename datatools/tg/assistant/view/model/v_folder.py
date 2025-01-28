from typing import AnyStr

from datatools.tg.assistant.view.model.v_element import VElement
from datatools.tui.treeview.rich_text import Style


# abstract
class VFolder(VElement):
    elements: list[VElement]

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.elements = []

    def set_elements(self, elements: list[VElement]):
        self.elements = elements
        for e in elements:
            e.parent = self

    def layout(self, line: int) -> int:
        line = super().layout(line)
        if self.collapsed:
            return line
        else:
            for item in self.elements:
                line = item.layout(line)
            self.size = line - self.line
            return line

    def indent_recursive(self, indent: int = None):
        if indent is None:
            indent = self.indent

        super().indent_recursive(indent)
        for e in self.elements:
            e.indent_recursive(indent + 2)

    def set_collapsed_recursive(self, collapsed: bool):
        super().set_collapsed_recursive(collapsed)
        for element in self.elements:
            element.set_collapsed_recursive(collapsed)

    # @override
    def spans(self, render_state=None) -> list[tuple[AnyStr, Style]]:
        return [(' ' * self.indent, self.style_for_plus_minus())] + self.spans_for_plus_minus() + self.rich_text()

    def show_plus_minus(self):
        return True

    def spans_for_plus_minus(self):
        return [('⊞ ' if self.collapsed else '⊟ ', self.style_for_plus_minus())] if self.show_plus_minus() \
            else [('⊡ ', self.style_for_plus_minus())]

    def style_for_plus_minus(self):
        return Style(0, (96, 96, 96))

    def __iter__(self):
        yield self
        if not self.collapsed:
            for e in self.elements:
                yield from e
