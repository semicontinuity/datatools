from dataclasses import dataclass

from datatools.tg.api.tg_api_message import TgApiMessage
from datatools.tg.api.tg_api_message_service import TgApiMessageService
from datatools.tg.assistant.model.tg_message import TgMessage


@dataclass
class TgTopic:
    id: int
    name: str
    tg_channel: 'TgChannel'

    latest_raw_messages: list[TgApiMessage | TgApiMessageService]
    latest_discussions: list[TgMessage]
