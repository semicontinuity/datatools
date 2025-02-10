from dataclasses import dataclass
from typing import List

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.model.tg_forum import TgForum


@dataclass
class TgData:
    tg_forums: List[TgForum]
    tg_channels: List[TgChannel]

    def save_caches(self):
        for c in self.tg_forums:
            c.save_caches()
        for c in self.tg_channels:
            c.save_caches()
