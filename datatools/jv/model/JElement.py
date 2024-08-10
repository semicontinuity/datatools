import sys
from typing import AnyStr, Tuple, List, Optional, Hashable, Sequence

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.tui.treeview.treenode import TreeNode


class JElement(TreeNode):

    indent: int
    key: Optional[str]
    padding: int

    def __init__(self, key: Optional[str] = None, indent=0, last_in_parent=True) -> None:
        super().__init__(last_in_parent)
        self.key = key
        self.indent = indent
        self.padding = 0

    def spans(self, render_state=None) -> List[Tuple[AnyStr, Style]]:
        return [(' ' * self.indent, Style())] + self.spans_for_field_label() + [self.rich_text()] + self.spans_for_comma()

    def spans_for_field_label(self) -> List[Tuple[AnyStr, Style]]:
        return [
            (f'"{self.key}"' + ' ' * self.get_padding(), Highlighting.CURRENT.for_field_label(self.key, self.indent, self.path())),
            (': ', Highlighting.CURRENT.for_colon()),
        ] if self.key is not None and type(self.key) is not int else []

    def spans_for_comma(self) -> List[Tuple[AnyStr, Style]]:
        return [] if self.last_in_parent else [(',', Highlighting.CURRENT.for_comma())]

    def rich_text(self) -> Tuple[AnyStr, Style]: pass

    def get_value(self): pass

    def get_value_element(self): pass

    def get_padding(self): return self.padding

    def path(self) -> List[Hashable]:
        path = []
        node = self
        while True:
            if node.parent is None:
                path.reverse()
                return path

            node = node.get_value_element()
            path.append(node.key)
            node = node.parent
