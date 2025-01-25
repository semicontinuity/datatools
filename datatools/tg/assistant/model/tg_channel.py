from dataclasses import dataclass

from datatools.tg.assistant.repository.channel_message_repository import ChannelMessageRepository


@dataclass
class TgChannel:
    id: int
    name: str
    tg_topics: list['TgTopic']
    channel_message_repository: ChannelMessageRepository
