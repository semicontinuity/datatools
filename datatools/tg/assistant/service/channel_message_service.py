import sys
from datetime import datetime

from sortedcontainers import SortedDict

from datatools.tg.api.tg_api_message import TgApiMessage
from datatools.tg.assistant.model.tg_ext_message import TgExtMessage
from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.repository.channel_api_message_repository import ChannelApiMessageRepository
from datatools.tg.assistant.repository.channel_ext_message_repository import ChannelExtMessageRepository
from datatools.tg.assistant.repository.channel_participants_repository import ChannelParticipantsRepository
from datatools.tg.assistant.service.message_summarizer_service import MessageSummarizerService


class ChannelMessageService:
    channel_ext_message_repository: ChannelExtMessageRepository
    channel_api_message_repository: ChannelApiMessageRepository
    channel_participants_repository: ChannelParticipantsRepository
    channel_id: int
    message_summarizer_service: MessageSummarizerService

    def __init__(
            self,
            channel_ext_message_repository: ChannelExtMessageRepository,
            channel_api_message_repository: ChannelApiMessageRepository,
            channel_participants_repository: ChannelParticipantsRepository,
            channel_id: int,
            message_summarizer_service: MessageSummarizerService,
    ) -> None:
        self.channel_ext_message_repository = channel_ext_message_repository
        self.channel_api_message_repository = channel_api_message_repository
        self.channel_participants_repository = channel_participants_repository
        self.channel_id = channel_id
        self.message_summarizer_service = message_summarizer_service

    def save_caches(self):
        self.channel_api_message_repository.save_cached()
        self.channel_ext_message_repository.save_cached()

    def get_latest_topic_discussion_forest(self, topic_id: int, since: str) -> list[TgMessage]:
        """
        :return: forest with "ROOTs" of discussions (with replies nested)
        """
        discussions = dict()
        raw_messages = self.channel_api_message_repository.get_latest_topic_raw_messages(topic_id, since)
        if not raw_messages:
            return []

        print(f'get_latest_topic_raw_discussions: min_id={raw_messages[0].id}, max_id={raw_messages[-1].id}', file=sys.stderr)

        for raw_message in raw_messages:
            child = None
            while True:
                m_id = raw_message.id

                discussion = discussions.get(m_id)
                if not discussion:
                    discussion = self.tg_message_for(raw_message)
                    discussions[m_id] = discussion

                elif child and child.id not in discussion.replies:
                    discussion.replies[child.id] = child

                if raw_message.reply_to and raw_message.reply_to.reply_to_msg_id:
                    raw_message = self.channel_api_message_repository.get_raw_message(raw_message.reply_to.reply_to_msg_id)

                    if type(raw_message) is TgApiMessage:
                        discussion.ext.is_reply = True
                        discussion.ext.is_reply_to = raw_message.id
                        child = discussion
                        continue
                break

        candidates = sorted(list(discussions.values()), key=lambda x: x.id)
        result = [x for x in candidates if not x.ext.is_reply]

        print(f'get_latest_topic_raw_discussions: {len(result)} roots', file=sys.stderr)
        return result

    def tg_message_for(self, raw_message):
        tg_ext_message = self.channel_ext_message_repository.get_message(raw_message.id)
        if tg_ext_message is None:
            tg_ext_message = TgExtMessage(raw_message.id)
            self.channel_ext_message_repository.put_message(tg_ext_message)

        tg_message = TgMessage(
            id=raw_message.id,
            ext=tg_ext_message,
            date=datetime.fromisoformat(raw_message.date),
            message=raw_message.message,
            replies=SortedDict()
        )

        if not tg_message.ext.summary and ('\n' in tg_message.message or len(tg_message.message) > 120):
            self.message_summarizer_service.request_summary(tg_message)

        if raw_message.from_id and raw_message.from_id.is_user():
            tg_message.from_user = self.channel_participants_repository.get_user(raw_message.from_id.user_id)

        return tg_message
