from sortedcontainers import SortedDict

from datatools.tg.api.tg_api_message import TgApiMessage
from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.repository.channel_message_repository import ChannelMessageRepository


class ChannelMessageService:
    channel_id: int
    repository: ChannelMessageRepository

    def __init__(self, repository: ChannelMessageRepository, channel_id: int) -> None:
        self.repository = repository
        self.channel_id = channel_id

    def get_latest_topic_raw_discussions(self, topic_id: int, since: str) -> list[TgMessage]:
        discussions = {}
        raw_messages = self.repository.get_latest_topic_raw_messages(topic_id, since)
        for m in raw_messages:
            child = None
            while True:
                m_id = m.id
                d = discussions.get(m_id)
                if not d:
                    d = TgMessage(m_id, m.message, SortedDict())
                    discussions[m_id] = d
                elif child and child.id not in d.replies:
                    d.replies[child.id] = child

                if m.reply_to and m.reply_to.reply_to_msg_id:
                    m = self.repository.get_raw_message(m.reply_to.reply_to_msg_id)
                    if type(m) is TgApiMessage:
                        d.is_reply = True
                        child = d
                        continue
                break

        candidates = sorted(list(discussions.values()), key=lambda x: x.id)
        return [x for x in candidates if not x.is_reply]
