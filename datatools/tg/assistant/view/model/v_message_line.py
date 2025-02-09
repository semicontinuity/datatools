from datatools.tg.assistant.view.model.v_element import VElement
from datatools.tui.treeview.rich_text import Style


class VMessageLine(VElement):

    def text_style(self) -> Style:
        return Style(attr=0, fg=(64, 160, 192), bg=(32, 48, 48))
