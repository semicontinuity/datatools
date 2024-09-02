from typing import Optional

from datatools.misc.expenses.viewer.highlighting.highlighting import Highlighting
from datatools.misc.expenses.viewer.model.JComplexElement import JComplexElement
from datatools.misc.expenses.viewer.model.JFolderSummary import JFolderSummary


class JFolder(JComplexElement):

    def __init__(self, value: float, key: Optional[str], indent=0, last_in_parent=True) -> None:
        super().__init__(value, key, indent, last_in_parent)
        self.start = JFolderSummary(value, key, indent=indent)
        self.start.parent = self

    def style(self):
        return Highlighting.CURRENT.for_number(True, self.indent)
