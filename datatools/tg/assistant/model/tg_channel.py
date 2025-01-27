from dataclasses import dataclass

from datatools.tg.assistant.repository.channel_message_repository import ChannelMessageRepository
from datatools.tg.assistant.service.channel_message_service import ChannelMessageService


@dataclass
class TgChannel:
    id: int
    name: str
    tg_topics: list['TgTopic']
    channel_message_repository: ChannelMessageRepository
    channel_message_service: ChannelMessageService

    def save_cache(self):
        self.channel_message_repository.save_cached()
