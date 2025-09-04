from datatools.jt.model.attributes import MASK_BOLD
from datatools.tg.assistant.view.model import V_MESSAGE_LINE_BG, V_READ_MESSAGE_FG, V_UNREAD_MESSAGE_FG
from datatools.tg.assistant.view.model.v_element import VElement
from datatools.tui.rich_text import Style


class VMessageLine(VElement):

    def __init__(self, text: str) -> None:
        super().__init__(text)

    def text_style(self) -> Style:
        boldness = 0 if self.parent.is_read() else MASK_BOLD
        return Style(attr=boldness, fg=V_READ_MESSAGE_FG if self.parent.is_read() else V_UNREAD_MESSAGE_FG, bg=V_MESSAGE_LINE_BG)
