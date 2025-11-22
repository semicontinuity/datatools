from dataclasses import dataclass

from datatools.tg.api.tg_api_message import TgApiMessage
from datatools.tg.api.tg_api_message_service import TgApiMessageService
from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.util.closeable import Closeable


@dataclass
class TgChannel:
    id: int
    name: str
    channel_message_service: Closeable

    latest_raw_messages: list[TgApiMessage | TgApiMessageService]
    latest_discussions: list[TgMessage]

    def close(self):
        self.channel_message_service.close()
