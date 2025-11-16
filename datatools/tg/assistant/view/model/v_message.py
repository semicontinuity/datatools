import os
from typing import AnyStr

from datatools.jt.model.attributes import MASK_ITALIC, MASK_BOLD, MASK_UNDERLINE
from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.service import message_is_short
from datatools.tg.assistant.view.model import V_READ_MESSAGE_FG, V_UNREAD_MESSAGE_FG, V_TIME
from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.coloring import hash_code, hash_to_rgb
from datatools.tui.rich_text import Style


class VMessage(VFolder):
    tg_message: TgMessage

    def __init__(self, tg_message: TgMessage, message_lines: list[str]) -> None:
        self.tg_message = tg_message
        self.message_lines = message_lines
        self.time = self.tg_message.date.astimezone().strftime("%b %d %H:%M")
        self.show_message_ids = os.environ.get('SHOW_MSG_IDS')
        self.show_summarized = os.environ.get('SHOW_SUMMARIZED')
        self.show_is_inferred_reply_to = os.environ.get('SHOW_IS_INFERRED_REPLY_TO')
        super().__init__(None)

    def count_unread_children(self):
        super().count_unread_children()
        if not self.is_read():
            parent = self.parent
            while parent:
                parent.unread_children += 1
                parent = parent.parent

    def rich_text(self) -> list[tuple[AnyStr, Style]]:
        is_read = self.is_read()
        boldness = 0 if is_read else MASK_BOLD
        user = self.tg_message.from_user.username if self.tg_message.from_user else '?'
        user = user or '?'

        return [
            (self.time, Style(boldness, V_TIME)),
            (f' <{self.tg_message.id}> ' if self.show_message_ids else '', Style()),
            (f' ({self.tg_message.ext.summarized}) ' if self.show_summarized else '', Style()),
            (f' [{self.tg_message.ext.is_inferred_reply_to}] ' if self.show_is_inferred_reply_to else '', Style()),
            (user, Style(MASK_UNDERLINE if self.tg_message.ext.is_inferred_reply_to else 0, hash_to_rgb(hash_code(user)))),
            (' ', Style()),
            self.summary_rich_text()
        ]

    def summary_rich_text(self):
        is_read = self.is_read()
        boldness = 0 if is_read else MASK_BOLD
        fg = V_READ_MESSAGE_FG if is_read else V_UNREAD_MESSAGE_FG
        summary_fg = V_READ_MESSAGE_FG if is_read else V_UNREAD_MESSAGE_FG

        if self.tg_message.ext.summary:
            return self.tg_message.ext.summary, Style(boldness | MASK_UNDERLINE, summary_fg)
        else:
            if len(self.message_lines) == 0:
                return self.tg_message.message, Style(boldness, fg)
            elif len(self.message_lines) == 1:
                return self.message_lines[0], Style(boldness, fg)
            elif self.collapsed:
                return self.tg_message.message.replace('\n', '  ') if message_is_short(self.tg_message.message) else self.message_lines[0], Style(boldness | MASK_ITALIC, fg)
            else:
                return '', Style(boldness | MASK_ITALIC, fg)

    # @override
    def show_plus_minus(self):
        return self.elements

    def style_for_plus_minus(self):
        return Style(0, (96, 96, 96))

    def is_read(self):
        return self.tg_message.ext.viewed

    # @override
    def visit_recursive(self):
        self.tg_message.ext.viewed = True
        for element in self.elements:
            element.visit_recursive()

    # @override
    def visit(self):
        if len(self.message_lines) <= 1 or not self.collapsed:
            self.tg_message.ext.viewed = True
