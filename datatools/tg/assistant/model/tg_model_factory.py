import pathlib

from telethon import TelegramClient
from telethon.tl.custom import Dialog

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.model.tg_data import TgData
from datatools.tg.assistant.model.tg_topic import TgTopic
from datatools.tg.assistant.repository.channel_api_message_repository import ChannelApiMessageRepository
from datatools.tg.assistant.repository.channel_ext_message_repository import ChannelExtMessageRepository
from datatools.tg.assistant.repository.channel_participants_repository import ChannelParticipantsRepository
from datatools.tg.assistant.repository.channel_repository import ChannelRepository
from datatools.tg.assistant.repository.channel_topic_repository import ChannelTopicRepository
from datatools.tg.assistant.service.channel_message_service import ChannelMessageService
from datatools.tg.assistant.service.message_summarizer_service import MessageSummarizerService


class TgModelFactory:

    def __init__(self, cache_folder: pathlib.Path, client: TelegramClient) -> None:
        self.cache_folder = cache_folder
        self.client = client
        self.channel_repository = ChannelRepository(cache_folder, client)
        self.channel_topic_repository = ChannelTopicRepository(client)
        self.message_summarizer_service = MessageSummarizerService()

    async def make_tg_data(self) -> TgData:
        dialogs = await self.channel_repository.get_dialogs()
        return TgData(
            [
                await self.make_tg_channel(dialog) for dialog in dialogs
            ]
        )

    async def make_tg_channel(self, dialog: Dialog):
        channel_id: int = dialog.id

        tg_channel = TgChannel(
            id=channel_id,
            name=dialog.name,
            tg_topics=[],
            channel_message_service=await self.make_channel_message_service(channel_id),
        )

        forum_topics = await self.channel_topic_repository.get_forum_topics(channel_id)
        tg_channel.tg_topics = [self.make_tg_topic(forum_topic, tg_channel) for forum_topic in forum_topics]

        return tg_channel

    def make_tg_topic(self, d, tg_channel: TgChannel):
        return TgTopic(id=d.id, name=d.title, tg_channel=tg_channel)

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
