from typing import AnyStr, Tuple, List, Optional, Any

from datatools.misc.tree_table.jv.highlighting.highlighting import Highlighting
from datatools.tui.treeview.rich_text import Style
from datatools.tui.treeview.treenode import TreeNode


class JElement(TreeNode):

    indent: int
    key: Optional[str]
    padding: int

    def __init__(self, value: Any, key: Optional[str] = None, indent=0, last_in_parent=True) -> None:
        super().__init__(last_in_parent)
        self.value = value
        self.key = key
        self.indent = indent
        self.padding = 0

    def spans(self, render_state=None) -> List[Tuple[AnyStr, Style]]:
        return [(' ' * self.indent, Style())] + self.spans_for_field_label() + [self.rich_text()]

    def spans_for_field_label(self) -> List[Tuple[AnyStr, Style]]:
        return [
            ('+ ' if self.collapsed else '- ', Highlighting.CURRENT.for_null()),
            (self.key + ' ' * self.get_padding(), Highlighting.CURRENT.for_field_label(self.key, self.indent)),
            (': ', Highlighting.CURRENT.for_colon()),
        ] if self.key is not None else []

    def rich_text(self) -> Tuple[AnyStr, Style]: pass

    def get_value(self): pass

    def get_value_element(self): pass

    def get_selector(self): pass

    def get_padding(self): return self.padding

    def is_folded(self): return True
