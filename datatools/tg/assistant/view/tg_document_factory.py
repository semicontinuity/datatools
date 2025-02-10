from datatools.tg.assistant.view.tg_document import TgDocument


class TgDocumentFactory:

    def make_document_for(self, root, footer):
        root.set_collapsed_recursive(True)
        root.collapsed = False
        doc = TgDocument(root)
        doc.footer = footer
        doc.layout()
        doc.count_unread_children()
        return doc
