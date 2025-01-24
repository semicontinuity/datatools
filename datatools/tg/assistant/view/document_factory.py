import pathlib
from typing import List

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.repository.channel_repository import ChannelRepository
from datatools.tg.assistant.repository.channel_topic_repository import ChannelTopicRepository
from datatools.tg.assistant.view.document import TgDocument
from datatools.tg.assistant.view.element_factory import TgElementFactory
from datatools.tg.assistant.view.model.VForum import VForum
from datatools.tg.assistant.view.model.VRoot import VRoot
from datatools.tg.assistant.view.model.VTopic import VTopic


class TgDocumentFactory:

    def __init__(self, cache_folder: pathlib.Path, client) -> None:
        self.cache_folder = cache_folder
        self.client = client
        self.channel_repository = ChannelRepository(cache_folder, client)
        self.topic_repository = ChannelTopicRepository(client)

    async def make_document(self) -> TgDocument:
        factory = TgElementFactory()
        root = await self.make_root()
        return self.make_document_for_model(root, "footer")

    async def make_root(self):
        await self.channel_repository.load()
        forums = [await self.make_forum(m) for m in self.channel_repository.models()]
        root = VRoot("telegram")
        root.set_elements(forums)
        root.indent_recursive()
        return root

    async def make_forum(self, tg_channel: TgChannel):
        v_forum = VForum(tg_channel)
        v_forum.set_elements(await self.make_topics(tg_channel))
        return v_forum

    async def make_topics(self, tg_channel: TgChannel) -> List[VTopic]:
        topic_models = await self.topic_repository.get_models(tg_channel)
        return [VTopic(t) for t in topic_models]

    def make_document_for_model(self, model, footer):
        model.set_collapsed_recursive(True)
        model.collapsed = False
        doc = TgDocument(model)
        doc.footer = footer
        doc.layout()
        return doc
