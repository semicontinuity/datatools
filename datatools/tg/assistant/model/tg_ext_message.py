
from dataclasses import dataclass


@dataclass
class TgExtMessage:
    id: int

    summary: str = None
    is_reply: bool = False
    is_reply_to: int = None
    is_attached: bool = False
    viewed: bool = False
