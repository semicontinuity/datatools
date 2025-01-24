import pathlib
from typing import List

from telethon.tl.functions.channels import GetForumTopicsRequest
from telethon.tl.types import ForumTopic
from telethon.tl.types.messages import ForumTopics

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.model.tg_topic import TgTopic


class ChannelTopicRepository:

    def __init__(self, client) -> None:
        self.client = client

    async def get_models(self, tg_channel: TgChannel) -> list[TgTopic]:
        ch = await self.client.get_entity(tg_channel.id)

        response: ForumTopics = await self.client(
            GetForumTopicsRequest(
                ch,
                offset_date=None,
                offset_id=0,
                offset_topic=0,
                limit=1000,
                q=''
            )
        )
        topics: List[ForumTopic] = response.topics
        return [TgTopic(id=d.id, name=d.title, tg_channel=tg_channel) for d in topics]
