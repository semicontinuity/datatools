from dataclasses import dataclass

from datatools.tg.assistant.api.tg_api_message_reply_header import TgApiMessageReplyHeader


@dataclass
class TgApiMessage:
    id: int
    date: str

    message: str
    reply_to: TgApiMessageReplyHeader = None
