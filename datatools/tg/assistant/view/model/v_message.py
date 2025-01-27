from typing import Tuple, AnyStr

from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VMessage(VFolder):
    tg_message: TgMessage

    def __init__(self, tg_message: TgMessage) -> None:
        self.tg_message = tg_message
        self.time = self.tg_message.date.astimezone().strftime("%b %d %H:%M")
        super().__init__(tg_message.message.replace('\n', ' | '))

    def rich_text(self) -> list[Tuple[AnyStr, Style]]:
        boldness = self.boldness()
        return [
            (self.time, Style(boldness, (64, 64, 64))),
            (' ', Style()),
            (self.tg_message.from_user.username if self.tg_message.from_user else '?', Style(boldness, (128, 128, 128))),
            (' ', Style()),
            (self.text, Style(boldness, (64, 160, 192))),
        ]

    # @override
    def show_plus_minus(self):
        return self.elements

    def style_for_plus_minus(self):
        return Style(0, (96, 96, 96))

    def boldness(self):
        return 0
