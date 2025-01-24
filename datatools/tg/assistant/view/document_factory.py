import pathlib

from datatools.tg.assistant.repository.channel_repository import ChannelRepository
from datatools.tg.assistant.view.document import TgDocument
from datatools.tg.assistant.view.element_factory import TgElementFactory
from datatools.tg.assistant.view.model.VForum import VForum
from datatools.tg.assistant.view.model.VRoot import VRoot
from datatools.tg.assistant.view.model.VTopic import VTopic


async def make_document(cache_folder: pathlib.Path, client) -> TgDocument:
    factory = TgElementFactory()

    channel_repository = ChannelRepository(cache_folder, client)
    await channel_repository.load()
    forums = [VForum(m) for m in channel_repository.models()]

    summary1 = factory.summary("summary 1")
    summary2 = factory.summary("summary 2")
    summary3 = factory.summary("summary 3")
    summary4 = factory.summary("summary 4")

    topic1 = VTopic("topic 1")
    topic1.set_elements([summary1, summary2])

    topic2 = VTopic("topic 2")
    topic2.set_elements([summary3, summary4])

    root = VRoot("telegram")
    root.set_elements(forums)
    root.indent_recursive(0)

    return make_document_for_model(root, "footer")


def make_document_for_model(model, footer):
    model.set_collapsed_recursive(True)
    model.collapsed = False
    doc = TgDocument(model)
    doc.footer = footer
    doc.layout()
    return doc
