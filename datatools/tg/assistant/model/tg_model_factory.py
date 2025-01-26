import pathlib

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.model.tg_data import TgData
from datatools.tg.assistant.model.tg_topic import TgTopic
from datatools.tg.assistant.repository.channel_message_repository import ChannelMessageRepository
from datatools.tg.assistant.repository.channel_participants_repository import ChannelParticipantsRepository
from datatools.tg.assistant.repository.channel_repository import ChannelRepository
from datatools.tg.assistant.repository.channel_topic_repository import ChannelTopicRepository


class TgModelFactory:

    def __init__(self, cache_folder: pathlib.Path, client, since: str) -> None:
        self.cache_folder = cache_folder
        self.client = client
        self.since = since
        self.channel_repository = ChannelRepository(cache_folder, client)
        self.channel_topic_repository = ChannelTopicRepository(client)

    async def make_tg_data(self):
        dialogs = await self.channel_repository.get_dialogs()
        return TgData(
            [
                await self.make_tg_channel(d) for d in dialogs
            ]
        )

    async def make_tg_channel(self, d):
        channel_message_repository = await self.make_channel_message_repository(d.id)
        tg_channel = TgChannel(
            id=d.id,
            name=d.name,
            tg_topics=[],
            channel_message_repository=channel_message_repository,
            participants=await self.make_channel_participants(d.id)
        )

        forum_topics = await self.channel_topic_repository.get_forum_topics(d.id)
        tg_channel.tg_topics = [TgTopic(id=d.id, name=d.title, tg_channel=tg_channel) for d in forum_topics]

        return tg_channel

    async def make_channel_message_repository(self, channel_id: int):
        r = ChannelMessageRepository(self.cache_folder, self.client, channel_id)
        await r.load()
        return r

    async def make_channel_participants(self, channel_id: int):
        r = ChannelParticipantsRepository(self.client, channel_id)
        return await r.load()
