from dataclasses import dataclass

from datatools.tg.assistant.model.tg_message import TgMessage


@dataclass
class TgTopic:
    id: int
    name: str
    tg_channel: 'TgChannel'

    def get_latest_discussions(self, since: str) -> list[TgMessage]:
        return self.tg_channel.channel_message_service.get_latest_topic_raw_discussions(self.id, since)