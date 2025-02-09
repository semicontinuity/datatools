from typing import List

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.model.tg_data import TgData
from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.model.tg_topic import TgTopic
from datatools.tg.assistant.view.model.v_element import VElement
from datatools.tg.assistant.view.model.v_forum import VForum
from datatools.tg.assistant.view.model.v_message import VMessage
from datatools.tg.assistant.view.model.v_root import VRoot
from datatools.tg.assistant.view.model.v_topic import VTopic


class TgViewFactory:

    def __init__(self, since) -> None:
        self.since = since

    def make_root(self, tg_data: TgData) -> VElement:
        root = VRoot("telegram")
        root.set_elements([self.make_forum(ch) for ch in tg_data.tg_channels])
        root.indent_recursive()
        return root

    def make_forum(self, tg_channel: TgChannel):
        v_forum = VForum(tg_channel)
        v_forum.set_elements([self.make_topic(t) for t in tg_channel.tg_topics])
        return v_forum

    def make_topic(self, tg_topic: TgTopic):
        v_topic = VTopic(tg_topic)
        v_topic.set_elements(self.make_messages(tg_topic))
        return v_topic

    def make_messages(self, tg_topic: TgTopic) -> List[VMessage]:
        return self.make_messages_list(
            tg_topic.get_latest_discussions(self.since)
        )

    def make_messages_list(self, discussions):
        return [self.make_message(t) for t in discussions]

    def make_message(self, tg_message: TgMessage) -> VMessage:
        v = VMessage(tg_message)
        v.set_elements(self.make_messages_list(tg_message.replies.values()))
        return v
