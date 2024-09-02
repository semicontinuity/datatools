from typing import AnyStr, Tuple, List, Optional, Hashable

from datatools.jv.highlighting.holder import get_current_highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.tui.treeview.treenode import TreeNode


class JElement(TreeNode):

    indent: int
    key: Optional[str]
    padding: int

    def __init__(self, key: Optional[str] = None) -> None:
        super().__init__(True)
        self.key = key
        self.indent = 0
        self.padding = 0

    def spans(self, render_state=None) -> List[Tuple[AnyStr, Style]]:
        return [(' ' * self.indent, Style())] + self.spans_for_field_label() + [self.rich_text()] + self.spans_for_comma()

    def spans_for_field_label(self) -> List[Tuple[AnyStr, Style]]:
        return [
            (f'"{self.key}"', get_current_highlighting().for_field_label(self.key, self.indent, self.path())),
            (' ' * self.get_padding(), Style()),
            (': ', get_current_highlighting().for_colon()),
        ] if self.key is not None and type(self.key) is not int else []

    def spans_for_comma(self) -> List[Tuple[AnyStr, Style]]:
        return [] if self.last_in_parent else [(',', get_current_highlighting().for_comma())]

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
