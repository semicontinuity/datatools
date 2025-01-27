from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VMessage(VFolder):
    tg_message: TgMessage

    def __init__(self, tg_message: TgMessage) -> None:
        self.tg_message = tg_message
        super().__init__(tg_message.message.replace('\n', ' | '))

    # @override
    def text_style(self) -> Style:
        return Style(0, (64, 160, 192))

    # @override
    def show_plus_minus(self):
        return self.tg_message.replies
