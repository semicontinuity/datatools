from dataclasses import dataclass

from datatools.tg.assistant.model.tg_message_reply_header import TgMessageReplyHeader


@dataclass
class TgMessage:
    id: int
    date: str

    message: str
    reply_to: TgMessageReplyHeader = None
