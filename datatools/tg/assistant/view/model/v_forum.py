from typing import Tuple, AnyStr

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VForum(VFolder):

    def __init__(self, tg_channel: TgChannel) -> None:
        super().__init__(tg_channel.name)
        self.tg_channel = tg_channel

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return self.tg_channel.name, Style(0, (224, 64, 128))
