from typing import Tuple, AnyStr

from datatools.tg.assistant.view.model.VFolder import VFolder
from datatools.tui.treeview.rich_text import Style


class VTopic(VFolder):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        return 'telegram', Style(0, (192, 192, 64))
