from dataclasses import dataclass
from sortedcontainers import SortedDict


@dataclass
class TgMessage:
    id: int
    message: str
    replies: SortedDict[int, 'TgMessage']
    is_reply: bool = False
    is_attached: bool = False
