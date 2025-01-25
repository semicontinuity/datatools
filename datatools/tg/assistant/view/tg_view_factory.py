from typing import List

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.model.tg_data import TgData
from datatools.tg.assistant.model.tg_topic import TgTopic
from datatools.tg.assistant.view.model.v_forum import VForum
from datatools.tg.assistant.view.model.v_root import VRoot
from datatools.tg.assistant.view.model.v_summary import VSummary
from datatools.tg.assistant.view.model.v_topic import VTopic


class TgViewFactory:

    def __init__(self, since) -> None:
        self.since = since

    def make_root(self, tg_data: TgData):
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

    def make_messages(self, tg_topic: TgTopic) -> List[VSummary]:
        messages = tg_topic.get_latest_messages(self.since)
        return [VSummary(t.message.replace('\n', ' | ')) for t in messages]
