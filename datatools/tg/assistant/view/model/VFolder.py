from typing import List, Tuple, AnyStr

from datatools.tg.assistant.view.model.VElement import VElement
from datatools.tui.treeview.rich_text import Style


class VFolder(VElement):
    elements: List[VElement]

    def set_elements(self, elements: List[VElement]):
        self.elements = elements
        for e in elements:
            e.parent = self

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return '{…}', Style(0, (64, 160, 192))

    def __iter__(self):
        yield self
        if not self.collapsed:
            for e in self.elements:
                yield from e
