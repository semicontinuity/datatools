from dataclasses import dataclass
from sortedcontainers import SortedDict


@dataclass
class TgMessage:
    id: int
    message: str
    replies: SortedDict[int, 'TgMessage']
    from_user: 'TgUser' = None
    is_reply: bool = False
    is_attached: bool = False
