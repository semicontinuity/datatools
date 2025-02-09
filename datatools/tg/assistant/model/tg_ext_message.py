
from dataclasses import dataclass


@dataclass
class TgExtMessage:
    id: int

    summary: str = None
    is_reply: bool = False
    is_reply_to: int = None
    viewed: bool = False

    inferred_replies: list[int] = None
    is_inferred_reply_to: int = None
