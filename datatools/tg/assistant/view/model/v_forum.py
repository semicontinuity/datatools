from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VForum(VFolder):

    def __init__(self, tg_channel: TgChannel) -> None:
        super().__init__(tg_channel.name)
        self.tg_channel = tg_channel

    def text_style(self) -> Style:
        return Style(0, (224, 64, 128))
