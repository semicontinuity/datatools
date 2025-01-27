from datatools.tg.assistant.model.tg_topic import TgTopic
from datatools.tg.assistant.view.model.v_folder import VFolder
from datatools.tui.treeview.rich_text import Style


class VTopic(VFolder):
    def __init__(self, tg_topic: TgTopic) -> None:
        super().__init__(tg_topic.name)
        self.tg_topic = tg_topic

    # @override
    def text_style(self) -> Style:
        return Style(0, (192, 192, 64)) if self.elements else Style(0, (96, 96, 32))

    # @override
    def show_plus_minus(self):
        return self.elements
