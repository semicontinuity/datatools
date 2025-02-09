from typing import AnyStr

from datatools.jt.model.attributes import MASK_ITALIC
from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.tui.treeview.rich_text import Style


class VMessage(VFolder):
    tg_message: TgMessage

    def __init__(self, tg_message: TgMessage, message_lines: list[str]) -> None:
        self.tg_message = tg_message
        self.message_lines = message_lines
        self.time = self.tg_message.date.astimezone().strftime("%b %d %H:%M")
        super().__init__(None)

    def rich_text(self) -> list[tuple[AnyStr, Style]]:
        boldness = self.boldness()

        res = [(self.time, Style(boldness, (80, 80, 80)))]

        user = None
        if self.tg_message.from_user:
            user = self.tg_message.from_user.username
        if user:
            res.append((' ', Style()))
            res.append((user, Style(boldness, hash_to_rgb(hash_code(user)))))

        res.append((' ', Style()))
        res.append(self.summary_rich_text())

        return res

    def summary_rich_text(self):
        if self.tg_message.ext.summary:
            return self.tg_message.ext.summary, Style(self.boldness(), (64, 160, 192))
        else:
            if len(self.message_lines) == 0:
                return self.tg_message.message, Style(self.boldness(), (64, 160, 192))
            elif len(self.message_lines) == 1:
                return self.message_lines[0], Style(self.boldness(), (64, 160, 192))
            else:
                return self.message_lines[0] if self.collapsed else '', Style(self.boldness() | MASK_ITALIC, (64, 160, 192))

    # @override
    def show_plus_minus(self):
        return self.elements

    def style_for_plus_minus(self):
        return Style(0, (96, 96, 96))

    def boldness(self):
        return 0
