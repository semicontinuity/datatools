from typing import Tuple, AnyStr

from datatools.tg.assistant.model.tg_topic import TgTopic
from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VTopic(VFolder):
    def __init__(self, tg_topic: TgTopic) -> None:
        super().__init__(tg_topic.name)
        self.tg_topic = tg_topic

    def rich_text(self) -> Tuple[AnyStr, Style]:
        return self.text, Style(0, (192, 192, 64))
