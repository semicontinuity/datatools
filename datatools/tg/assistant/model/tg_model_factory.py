import pathlib
import sys

from telethon import TelegramClient
from telethon.tl.custom import Dialog
from yndx.st.lib.llm.gradio import Gradio

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.model.tg_data import TgData
from datatools.tg.assistant.model.tg_topic import TgTopic
from datatools.tg.assistant.repository.channel_api_message_repository import ChannelApiMessageRepository
from datatools.tg.assistant.repository.channel_ext_message_repository import ChannelExtMessageRepository
from datatools.tg.assistant.repository.channel_participants_repository import ChannelParticipantsRepository
from datatools.tg.assistant.repository.channel_repository import ChannelRepository
from datatools.tg.assistant.repository.channel_topic_repository import ChannelTopicRepository
from datatools.tg.assistant.service.channel_message_service import ChannelMessageService
from datatools.tg.assistant.service.discussion_classifier import DiscussionClassifier
from datatools.tg.assistant.service.discussion_forest_flattener import flat_discussion_forest
from datatools.tg.assistant.service.message_summarizer_service import MessageSummarizerService
from datatools.tg.assistant.service.topic_messages_weaver import TopicMessagesWeaver


class TgModelFactory:

    def __init__(self, cache_folder: pathlib.Path, client: TelegramClient, since: str) -> None:
        self.cache_folder = cache_folder
        self.client = client
        self.channel_repository = ChannelRepository(cache_folder, client)
        self.channel_topic_repository = ChannelTopicRepository(client)
        self.message_summarizer_service = MessageSummarizerService()
        self.topic_messages_weaver = TopicMessagesWeaver(DiscussionClassifier(Gradio()))
        self.since = since

    async def make_tg_data(self) -> TgData:
        dialogs = await self.channel_repository.get_dialogs()
        return TgData(
            [
                await self.make_tg_channel(dialog) for dialog in dialogs
            ]
        )

    async def make_tg_channel(self, dialog: Dialog):
        channel_id: int = dialog.id

        forum = dialog.entity.forum
        tg_channel = TgChannel(
            id=channel_id,
            forum=forum,
            name=dialog.name,
            tg_topics=[],
            channel_message_service=await self.make_channel_message_service(channel_id),
        )

        if forum:
            forum_topics = await self.channel_topic_repository.get_forum_topics(channel_id)
            tg_channel.tg_topics = [self.make_tg_topic(forum_topic, tg_channel) for forum_topic in forum_topics]

        return tg_channel

    def make_tg_topic(self, forum_topic, tg_channel: TgChannel):
        messages = tg_channel.channel_message_service.channel_api_message_repository.get_latest_topic_raw_messages(forum_topic.id, self.since)
        discussion_forest = tg_channel.channel_message_service.make_latest_topic_discussion_forest(messages)
        flat_discussions = flat_discussion_forest(discussion_forest)
        inference_done = all(flat_discussion.ext.inference_done() for flat_discussion in flat_discussions)
        print(f'inference already done: {inference_done}, channel_id: {tg_channel.id}, topic_id: {forum_topic.id}', file=sys.stderr)
        if not inference_done:
            self.topic_messages_weaver.submit(flat_discussions)

        return TgTopic(
            id=forum_topic.id,
            name=forum_topic.title,
            tg_channel=tg_channel,
            latest_raw_messages=messages,
            latest_discussions=discussion_forest
        )

    async def make_channel_message_service(self, channel_id: int):
        channel_participants_repository = ChannelParticipantsRepository(self.client, channel_id)
        await channel_participants_repository.load()

        channel_api_message_repository = ChannelApiMessageRepository(self.cache_folder, self.client, channel_id)
        await channel_api_message_repository.load()

        channel_ext_message_repository = ChannelExtMessageRepository(self.cache_folder, channel_id)
        channel_ext_message_repository.load_cached()

        return ChannelMessageService(
            channel_ext_message_repository,
            channel_api_message_repository,
            channel_participants_repository,
            channel_id,
            self.message_summarizer_service
        )

    def close(self):
        self.message_summarizer_service.stop()
        self.topic_messages_weaver.stop()
