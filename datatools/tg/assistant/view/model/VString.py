from typing import Tuple, AnyStr, Any

from datatools.tg.assistant.view.model.VElement import VElement
from datatools.tui.treeview.rich_text import Style


class JString(VElement):

    def __init__(self, value: Any) -> None:
        super().__init__()
        self.value = value

    # @override
    def rich_text(self) -> Tuple[AnyStr, Style]:
        return self.value, Style(0, (64, 160, 192))
