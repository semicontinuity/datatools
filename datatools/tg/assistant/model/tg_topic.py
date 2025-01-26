from dataclasses import dataclass
from typing import List

from datatools.tg.assistant.api.tg_api_message import TgApiMessage


@dataclass
class TgTopic:
    id: int
    name: str
    tg_channel: 'TgChannel'

    def get_latest_messages(self, since: str) -> List[TgApiMessage]:
        return self.tg_channel.channel_message_repository.get_latest_topic_raw_messages(self.id, since)