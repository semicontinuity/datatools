import sys

from sortedcontainers import SortedDict

from datatools.tg.api.tg_api_message import TgApiMessage
from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.repository.channel_message_repository import ChannelMessageRepository
from datatools.tg.assistant.repository.channel_participants_repository import ChannelParticipantsRepository


class ChannelMessageService:
    repository: ChannelMessageRepository
    channel_participants_repository: ChannelParticipantsRepository
    channel_id: int

    def __init__(self, repository: ChannelMessageRepository, channel_participants_repository: ChannelParticipantsRepository, channel_id: int) -> None:
        self.repository = repository
        self.channel_participants_repository = channel_participants_repository
        self.channel_id = channel_id

    def get_latest_topic_raw_discussions(self, topic_id: int, since: str) -> list[TgMessage]:
        discussions = {}
        raw_messages = self.repository.get_latest_topic_raw_messages(topic_id, since)
        for raw_message in raw_messages:
            print('RAW ', raw_message, file=sys.stderr)

            child = None
            while True:
                m_id = raw_message.id
                d = discussions.get(m_id)
                if not d:
                    d = TgMessage(m_id, raw_message.message, SortedDict())
                    if raw_message.from_id and raw_message.from_id.is_user():
                        d.from_user = self.channel_participants_repository.get_user(raw_message.from_id.user_id)

                    discussions[m_id] = d
                elif child and child.id not in d.replies:
                    d.replies[child.id] = child

                if raw_message.reply_to and raw_message.reply_to.reply_to_msg_id:
                    raw_message = self.repository.get_raw_message(raw_message.reply_to.reply_to_msg_id)
                    if type(raw_message) is TgApiMessage:
                        d.is_reply = True
                        child = d
                        continue
                break

        candidates = sorted(list(discussions.values()), key=lambda x: x.id)
        return [x for x in candidates if not x.is_reply]
