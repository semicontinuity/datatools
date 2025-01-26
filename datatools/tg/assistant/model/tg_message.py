from dataclasses import dataclass


@dataclass
class TgMessage:
    id: int
    message: str
    replies: list['TgMessage']
