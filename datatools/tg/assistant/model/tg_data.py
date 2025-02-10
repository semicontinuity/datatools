from dataclasses import dataclass
from typing import List

from datatools.tg.assistant.model.tg_forum import TgForum


@dataclass
class TgData:
    tg_forums: List[TgForum]

    def save_caches(self):
        for ch in self.tg_forums:
            ch.save_caches()
