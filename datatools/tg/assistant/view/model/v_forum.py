from datatools.tg.assistant.model.tg_forum import TgForum
from datatools.tg.assistant.view.model import V_FORUM_FG
from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VForum(VFolder):

    def __init__(self, tg_channel: TgForum) -> None:
        super().__init__(tg_channel.name)
        self.tg_channel = tg_channel

    def text_style(self) -> Style:
        return Style(0, V_FORUM_FG)
