
from dataclasses import dataclass


@dataclass
class TgExtMessage:
    id: int

    viewed: bool = False
    summary: str = None

    is_reply_to: int = None
    is_inferred_reply_to: int = None
    inferred_replies: list[int] = None
