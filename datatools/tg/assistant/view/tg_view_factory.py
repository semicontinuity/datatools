from typing import List

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.model.tg_data import TgData
from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.model.tg_topic import TgTopic
from datatools.tg.assistant.view.long_message_splitter import split_text_into_lines0
from datatools.tg.assistant.view.model.v_channel import VChannel
from datatools.tg.assistant.view.model.v_element import VElement
from datatools.tg.assistant.view.model.v_forum import VForum
from datatools.tg.assistant.view.model.v_message import VMessage
from datatools.tg.assistant.view.model.v_message_line import VMessageLine
from datatools.tg.assistant.view.model.v_root import VRoot
from datatools.tg.assistant.view.model.v_topic import VTopic


class TgViewFactory:

    def make_root(self, tg_data: TgData) -> VElement:
        root = VRoot("telegram")
        root.set_elements([self.make_forum_or_channel(ch) for ch in tg_data.tg_channels])
        root.indent_recursive()
        return root

    def make_forum_or_channel(self, tg_channel: TgChannel):
        if tg_channel.forum:
            return self.make_forum(tg_channel)
        else:
            return self.make_channel(tg_channel)

    def make_channel(self, tg_channel: TgChannel):
        v_channel = VChannel(tg_channel)
        return v_channel

    def make_forum(self, tg_channel: TgChannel):
        v_forum = VForum(tg_channel)
        v_forum.set_elements([self.make_topic(t) for t in tg_channel.tg_topics])
        return v_forum

    def make_topic(self, tg_topic: TgTopic):
        v_topic = VTopic(tg_topic)
        v_topic.set_elements(self.make_messages(tg_topic))
        return v_topic

    def make_messages(self, tg_topic: TgTopic) -> List[VMessage]:
        return self.make_messages_list(tg_topic.latest_discussions)

    def make_messages_list(self, discussions) -> list[VMessage]:
        return [self.make_message(t) for t in discussions]

    def make_message(self, tg_message: TgMessage) -> VMessage:
        sub_messages = self.make_messages_list(tg_message.replies.values())

        message_lines = split_text_into_lines0(tg_message.message)
        if len(message_lines) <= 1:
            children = sub_messages
        else:
            width = max(len(l) for l in message_lines)
            children = [VMessageLine('▏' + l + ' ' * (width - len(l)) + '▕') for l in message_lines] + sub_messages

        v = VMessage(tg_message, message_lines)
        v.set_elements(children)
        return v
