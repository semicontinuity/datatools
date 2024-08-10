from typing import Hashable, List

from datatools.jv.model import JElement
from datatools.tui.treeview.rich_text import Style


class Highlighting:
    def for_null(self) -> Style: return Style()

    def for_true(self) -> Style: return Style()

    def for_false(self) -> Style: return Style()

    def for_number(self) -> Style: return Style()

    def for_string(self, node: JElement) -> Style: return Style()

    def for_comma(self) -> Style: return Style()

    def for_colon(self) -> Style: return Style()

    def for_curly_braces(self) -> Style: return Style()

    def for_square_brackets(self) -> Style: return Style()

    def for_field_label(self, label: str, indent: int, path: List[Hashable]) -> Style: return Style()
