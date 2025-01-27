from datatools.tg.assistant.view.model.v_element import VElement
from datatools.tui.treeview.rich_text import Style


class VSummary(VElement):

    # @override
    def text_style(self) -> Style:
        return Style(0, (64, 160, 192))
