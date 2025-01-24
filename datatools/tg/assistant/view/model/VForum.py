from typing import Tuple, AnyStr

from datatools.tg.assistant.view.model.VFolder import VFolder
from datatools.tui.treeview.rich_text import Style


class VForum(VFolder):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        return 'telegram', Style(0, (224, 64, 128))
