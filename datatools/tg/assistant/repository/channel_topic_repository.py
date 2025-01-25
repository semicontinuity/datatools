from telethon.tl.functions.channels import GetForumTopicsRequest
from telethon.tl.types import ForumTopic
from telethon.tl.types.messages import ForumTopics


class ChannelTopicRepository:

    def __init__(self, client) -> None:
        self.client = client

    async def get_forum_topics(self, tg_channel_id: int) -> list[ForumTopic]:
        ch = await self.client.get_entity(tg_channel_id)

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
        return response.topics
