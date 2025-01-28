from dataclasses import dataclass
from typing import List

from datatools.tg.assistant.model.tg_channel import TgChannel


@dataclass
class TgData:
    tg_channels: List[TgChannel]

    def save_caches(self):
        for ch in self.tg_channels:
            ch.save_caches()
