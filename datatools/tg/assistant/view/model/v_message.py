import sys
from typing import AnyStr

from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VMessage(VFolder):
    tg_message: TgMessage

    def __init__(self, tg_message: TgMessage) -> None:
        self.tg_message = tg_message

        self.time = self.tg_message.date.astimezone().strftime("%b %d %H:%M")
        super().__init__(tg_message.ext.summary or tg_message.message)

    def rich_text(self) -> list[tuple[AnyStr, Style]]:
        boldness = self.boldness()

        res = [(self.time, Style(boldness, (80, 80, 80)))]

        user = None
        if self.tg_message.from_user:
            user = self.tg_message.from_user.username
        if user:
            res.append((' ', Style()))
            res.append((user, Style(boldness, (128, 128, 128))))

        res.append((' ', Style()))
        res.append((self.text, Style(boldness, (64, 160, 192))))

        return res

    # @override
    def show_plus_minus(self):
        return self.elements

    def style_for_plus_minus(self):
        return Style(0, (96, 96, 96))

    def boldness(self):
        return 0
