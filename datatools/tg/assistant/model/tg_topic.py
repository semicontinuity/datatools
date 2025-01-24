from dataclasses import dataclass

from datatools.tg.assistant.model.tg_channel import TgChannel


@dataclass
class TgTopic:
    id: int
    name: str
    tg_channel: TgChannel