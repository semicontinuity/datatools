from dataclasses import dataclass
from typing import List

from datatools.tg.assistant.api.tg_api_message import TgApiMessage
from datatools.tg.assistant.model.tg_channel import TgChannel


@dataclass
class TgTopic:
    id: int
    name: str
    tg_channel: TgChannel

    def get_latest_messages(self, since: str) -> List[TgApiMessage]:
        return self.tg_channel.repository.get_latest_topic_messages(self.id, since)