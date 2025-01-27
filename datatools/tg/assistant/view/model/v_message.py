from typing import Tuple, AnyStr

from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VMessage(VFolder):
    tg_message: TgMessage

    def __init__(self, tg_message: TgMessage) -> None:
        self.tg_message = tg_message
        self.time = self.tg_message.date.astimezone().strftime("%b %d %H:%M ")
        super().__init__(tg_message.message.replace('\n', ' | '))

    def rich_text(self) -> list[Tuple[AnyStr, Style]]:
        return [(self.time, Style(0, (64, 64, 64))), (self.text, self.text_style())]

    # @override
    def text_style(self) -> Style:
        return Style(0, (64, 160, 192))

    # @override
    def show_plus_minus(self):
        return self.elements

    def style_for_plus_minus(self):
        return Style(0, (96, 96, 96))
