from typing import Tuple, AnyStr

from datatools.tg.assistant.view.model.v_element import VElement
from datatools.tui.treeview.rich_text import Style


class VMessage(VElement):

    # @override
    def rich_text(self) -> Tuple[AnyStr, Style]:
        return self.text, Style(0, (64, 160, 192))
