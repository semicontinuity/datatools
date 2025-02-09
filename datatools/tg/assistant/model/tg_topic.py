from dataclasses import dataclass

from datatools.tg.assistant.model.tg_message import TgMessage


@dataclass
class TgTopic:
    id: int
    name: str
    tg_channel: 'TgChannel'

    def get_latest_discussions(self, since: str) -> list[TgMessage]:
        raw_messages = self.tg_channel.channel_message_service.channel_api_message_repository.get_latest_topic_raw_messages(self.id, since)
        return self.tg_channel.channel_message_service.make_latest_topic_discussion_forest(raw_messages)
