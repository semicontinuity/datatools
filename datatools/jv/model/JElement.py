from typing import AnyStr, Tuple, List, Optional

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.tui.treeview.model.TreeNode import TreeNode


class JElement(TreeNode):

    indent: int
    key: Optional[str]
    padding: int

    def __init__(self, key: Optional[str] = None, indent=0, last_in_parent=True) -> None:
        super().__init__(last_in_parent)
        self.key = key
        self.indent = indent
        self.padding = 0

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        return [(' ' * self.indent, Style())] + self.spans_for_field_label() + [self.rich_text()] + self.spans_for_comma()

    def spans_for_field_label(self) -> List[Tuple[AnyStr, Style]]:
        return [
            (f'"{self.key}"' + ' ' * self.padding, Highlighting.CURRENT.for_field_label(self.key)),
            (': ', Highlighting.CURRENT.for_colon()),
        ] if self.key is not None else []

    def spans_for_comma(self) -> List[Tuple[AnyStr, Style]]:
        return [] if self.last_in_parent else [(',', Highlighting.CURRENT.for_comma())]
