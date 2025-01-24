import pathlib
from typing import List

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.model.tg_topic import TgTopic
from datatools.tg.assistant.repository.channel_repository import ChannelRepository
from datatools.tg.assistant.repository.channel_topic_repository import ChannelTopicRepository
from datatools.tg.assistant.view.document import TgDocument
from datatools.tg.assistant.view.model.VForum import VForum
from datatools.tg.assistant.view.model.VRoot import VRoot
from datatools.tg.assistant.view.model.VSummary import VSummary
from datatools.tg.assistant.view.model.VTopic import VTopic


class TgDocumentFactory:

    def __init__(self, cache_folder: pathlib.Path, client) -> None:
        self.cache_folder = cache_folder
        self.client = client
        self.channel_repository = ChannelRepository(cache_folder, client)
        self.topic_repository = ChannelTopicRepository(client)

    async def make_document(self) -> TgDocument:
        root = await self.make_root()
        return self.make_document_for_model(root, "footer")

    async def make_root(self):
        root = VRoot("telegram")
        root.set_elements(await self.make_forums())
        root.indent_recursive()
        return root

    async def make_forums(self) -> List[VForum]:
        return [await self.make_forum(m) for m in await self.channel_repository.get_models()]

    async def make_forum(self, tg_channel: TgChannel):
        v_forum = VForum(tg_channel)
        v_forum.set_elements(await self.make_topics(tg_channel))
        return v_forum

    async def make_topics(self, tg_channel: TgChannel) -> List[VTopic]:
        return [self.make_topic(t) for t in await self.topic_repository.get_models(tg_channel)]

    def make_topic(self, tg_topic: TgTopic):
        v_topic = VTopic(tg_topic)
        v_topic.set_elements([])
        return v_topic

    async def make_messages(self, tg_topic: TgTopic) -> List[VTopic]:
        # return [VSummary(t) for t in topic_models.na]
        return []

    def make_document_for_model(self, model, footer):
        model.set_collapsed_recursive(True)
        model.collapsed = False
        doc = TgDocument(model)
        doc.footer = footer
        doc.layout()
        return doc
