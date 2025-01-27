from typing import List, Tuple, AnyStr

from datatools.tg.assistant.view.model.v_element import VElement
from datatools.tui.treeview.rich_text import Style


class VFolder(VElement):
    elements: List[VElement]

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.elements = []

    def set_elements(self, elements: List[VElement]):
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
    def spans(self, render_state=None) -> List[Tuple[AnyStr, Style]]:
        return [(' ' * self.indent, Style())] + [self.rich_text()]

    def text_style(self) -> Style:
        return Style(0, (64, 160, 192))

    def __iter__(self):
        yield self
        if not self.collapsed:
            for e in self.elements:
                yield from e
