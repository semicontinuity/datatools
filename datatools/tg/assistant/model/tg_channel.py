from dataclasses import dataclass

from datatools.tg.assistant.repository.channel_message_repository import ChannelMessageRepository


@dataclass
class TgChannel:
    id: int
    name: str
    repository: ChannelMessageRepository
