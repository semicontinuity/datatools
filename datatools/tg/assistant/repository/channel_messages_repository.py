import json
import pathlib
from typing import List, Dict, Union

from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.model.tg_message_service import TgMessageService
from datatools.util.dataclasses import dataclass_from_dict


class ChannelMessageRepository:
    file: pathlib.Path
    data: Dict[int, Dict]
    max_id: int

    def __init__(self, cache_folder: pathlib.Path, channel_id: int) -> None:
        self.file = cache_folder / 'jsondb' / 'channels' / str(channel_id) / 'messages.jsonl'

    def load(self):
        with open(self.file, 'r') as file:
            self.data = {}

            for line in file:
                j = json.loads(line)
                self.max_id = j['id']
                self.data[self.max_id] = j

    def get_max_id(self):
        return self.max_id

    def get_message(self, message_id: int) -> Union[TgMessage, TgMessageService]:
        j = self.data.get(message_id)
        if j is None:
            return None
        if j['_'] == 'Message':
            return dataclass_from_dict(TgMessage, j)
        else:
            return dataclass_from_dict(TgMessageService, j)

    def get_latest_messages(self, date_gte: str) -> List[Union[TgMessage, TgMessageService]]:
        res = []
        i = self.max_id

        while i > 0:
            m = self.get_message(i)
            if m is not None:
                if m.date < date_gte:
                    break
                res.append(m)
            i -= 1

        res.reverse()
        return res