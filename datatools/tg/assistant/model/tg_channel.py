from dataclasses import dataclass

from datatools.tg.api.tg_api_message import TgApiMessage
from datatools.tg.api.tg_api_message_service import TgApiMessageService
from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.service.channel_message_service import ChannelMessageService


@dataclass
class TgChannel:
    id: int
    name: str
    channel_message_service: ChannelMessageService

    latest_raw_messages: list[TgApiMessage | TgApiMessageService]
    latest_discussions: list[TgMessage]

    def save_caches(self):
        self.channel_message_service.save_caches()
