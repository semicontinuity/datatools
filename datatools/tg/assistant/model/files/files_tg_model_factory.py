import pathlib
import sys

from telethon import TelegramClient
from telethon.tl.custom import Dialog
from yndx.llm.factory import llm

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.model.tg_forum import TgForum
from datatools.tg.assistant.model.tg_model_factory import TgModelFactory
from datatools.tg.assistant.model.tg_root_objects import TgRootObjects
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


class FilesTgModelFactory(TgModelFactory):
    client: TelegramClient

    def __init__(self, client: TelegramClient, since: str, cache_folder: pathlib.Path) -> None:
        super().__init__(client)
        self.cache_folder = cache_folder

        self.channel_repository = ChannelRepository(cache_folder, client)
        self.channel_topic_repository = ChannelTopicRepository(client)
        self.message_summarizer_service = MessageSummarizerService()
        self.topic_messages_weaver = TopicMessagesWeaver(DiscussionClassifier(llm()))
        self.since = since

    # @override
    async def make_tg_root_objects(self) -> TgRootObjects:
        dialogs = await self.channel_repository.get_dialogs()
        return TgRootObjects(
            tg_forums = [await self.__make_tg_forum(dialog) for dialog in dialogs if dialog.entity.forum],
            tg_channels = [await self.__make_tg_channel(dialog) for dialog in dialogs if not dialog.entity.forum],
        )

    async def __make_tg_channel(self, dialog: Dialog) -> TgChannel:
        channel_id: int = dialog.id
        channel_message_service = await self.make_channel_message_service(channel_id)

        messages = channel_message_service.channel_api_message_repository.get_latest_raw_messages(self.since)
        discussion_forest = channel_message_service.make_latest_topic_discussion_forest(messages)
        flat_discussions = flat_discussion_forest(discussion_forest)
        inference_done = all(flat_discussion.ext.inference_done() for flat_discussion in flat_discussions)
        print(f'inference already done: {inference_done}, channel_id: {channel_id}', file=sys.stderr)
        if not inference_done:
            self.topic_messages_weaver.submit(flat_discussions)

        return TgChannel(
            id=channel_id,
            name=dialog.name,
            channel_message_service=channel_message_service,
            latest_raw_messages=messages,
            latest_discussions=discussion_forest
        )

    async def __make_tg_forum(self, dialog: Dialog) -> TgForum:
        channel_id: int = dialog.id

        tg_forum = TgForum(
            id=channel_id,
            name=dialog.name,
            tg_topics=[],
            channel_message_service=await self.make_channel_message_service(channel_id),
        )

        forum_topics = await self.channel_topic_repository.get_forum_topics(channel_id)
        tg_forum.tg_topics = [self.__make_tg_topic(forum_topic, tg_forum) for forum_topic in forum_topics]

        return tg_forum

    def __make_tg_topic(self, forum_topic, tg_forum: TgForum):
        messages = tg_forum.channel_message_service.channel_api_message_repository.get_latest_topic_raw_messages(forum_topic.id, self.since)
        discussion_forest = tg_forum.channel_message_service.make_latest_topic_discussion_forest(messages)
        flat_discussions = flat_discussion_forest(discussion_forest)
        inference_done = all(flat_discussion.ext.inference_done() for flat_discussion in flat_discussions)
        print(f'inference already done: {inference_done}, channel_id: {tg_forum.id}, topic_id: {forum_topic.id}', file=sys.stderr)
        if not inference_done:
            self.topic_messages_weaver.submit(flat_discussions)

        return TgTopic(
            id=forum_topic.id,
            name=forum_topic.title,
            tg_channel=tg_forum,
            latest_raw_messages=messages,
            latest_discussions=discussion_forest
        )

    # @override
    async def make_channel_message_service(self, channel_id: int) -> ChannelMessageService:
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

    # @override
    def close(self):
        self.message_summarizer_service.stop()
        self.topic_messages_weaver.stop()
