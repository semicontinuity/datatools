from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VRoot(VFolder):

    # @override
    def text_style(self) -> Style:
        return Style(0, (64, 192, 64))
