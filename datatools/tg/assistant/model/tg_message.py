import datetime
from dataclasses import dataclass

from sortedcontainers import SortedDict

from datatools.tg.assistant.model.tg_ext_message import TgExtMessage
from datatools.tg.assistant.model.tg_user import TgUser


@dataclass
class TgMessage:
    id: int

    ext: TgExtMessage

    date: datetime.datetime
    message: str
    replies: SortedDict[int, 'TgMessage']
    from_user: TgUser = None

    def get_username(self):
        if not self.from_user:
            return None
        else:
            return self.from_user.username
