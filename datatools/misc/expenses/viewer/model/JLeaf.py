from datatools.misc.expenses.viewer.highlighting.highlighting import Highlighting
from datatools.misc.expenses.viewer.model.JPrimitiveElement import JPrimitiveElement
from datatools.tui.rich_text import Style


class JLeaf(JPrimitiveElement[str]):

    def style(self) -> Style:
        return Highlighting.CURRENT.for_number(False, self.indent)
