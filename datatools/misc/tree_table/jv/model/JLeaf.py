from datatools.misc.tree_table.jv.highlighting.highlighting import Highlighting
from datatools.misc.tree_table.jv.model.JPrimitiveElement import JPrimitiveElement
from datatools.tui.treeview.rich_text import Style


class JLeaf(JPrimitiveElement[str]):

    def style(self) -> Style:
        return Highlighting.CURRENT.for_number(False, self.indent)
