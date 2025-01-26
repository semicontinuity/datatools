from dataclasses import dataclass

from datatools.tg.assistant.api.tg_api_message_reply_header import TgApiMessageReplyHeader
from datatools.tg.assistant.api.tg_api_peer import TgApiPeer


@dataclass
class TgApiMessage:
    id: int
    date: str

    message: str
    reply_to: TgApiMessageReplyHeader = None
    from_id: TgApiPeer = None