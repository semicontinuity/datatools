from typing import Tuple, AnyStr, Optional, Any, List

from datatools.misc.tree_table.jv import format_float
from datatools.misc.tree_table.jv.highlighting.highlighting import Highlighting
from datatools.misc.tree_table.jv.model.JFolderSummary import JFolderSummary
from datatools.misc.tree_table.jv.model.JComplexElement import JComplexElement
from datatools.tui.treeview.rich_text import Style


class JFolder(JComplexElement):

    def __init__(self, value: float, key: Optional[str], indent=0, last_in_parent=True) -> None:
        super().__init__(value, key, indent, last_in_parent)
        self.start = JFolderSummary(value, key, indent=indent)
        self.start.parent = self

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return format_float(self.value), Highlighting.CURRENT.for_number()
