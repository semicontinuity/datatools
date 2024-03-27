from typing import Tuple, AnyStr

from datatools.misc.tree_table.jv.highlighting.highlighting import Highlighting
from datatools.misc.tree_table.jv.model.JSyntaxElement import JSyntaxElement
from datatools.tui.treeview.rich_text import Style


class JFolderSummary(JSyntaxElement):

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return f'{self.value:g}', Highlighting.CURRENT.for_number()
