from typing import Tuple, AnyStr

from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VRoot(VFolder):
    def rich_text(self) -> Tuple[AnyStr, Style]:
        return 'telegram', Style(0, (64, 192, 64))
