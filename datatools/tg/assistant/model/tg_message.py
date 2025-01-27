import datetime
from dataclasses import dataclass

from sortedcontainers import SortedDict


@dataclass
class TgMessage:
    id: int
    date: datetime.datetime
    message: str
    replies: SortedDict[int, 'TgMessage']
    from_user: 'TgUser' = None
    is_reply: bool = False
    is_reply_to: int = None
    is_attached: bool = False
    viewed: bool = False

    def get_username(self):
        if not self.from_user:
            return None
        else:
            return self.from_user.username
