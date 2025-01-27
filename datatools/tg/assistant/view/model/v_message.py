from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VMessage(VFolder):

    # @override
    def text_style(self) -> Style:
        return Style(0, (64, 160, 192))
