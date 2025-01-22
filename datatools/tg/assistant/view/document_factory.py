from datatools.tg.assistant.view.document import TgDocument
from datatools.tg.assistant.view.element_factory import TgElementFactory
from datatools.tg.assistant.view.model.VFolder import VFolder


def make_document() -> TgDocument:
    factory = TgElementFactory()

    root = VFolder()
    root.set_elements([factory.string("item", None)])
    root.indent_recursive(0)

    return make_document_for_model(root, "footer")


def make_document_for_model(model, footer):
    model.set_collapsed_recursive(True)
    model.collapsed = False
    doc = TgDocument(model)
    doc.footer = footer
    return doc
