import json
import pathlib
from typing import List, Dict, Union

from datatools.tg.assistant.api.tg_api_message import TgApiMessage
from datatools.tg.assistant.api.tg_api_message_service import TgApiMessageService
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

    def resolve_topic_id(self, m: Union[TgApiMessage, TgApiMessageService]) -> int:
        if m is None:
            return None
        elif type(m) == TgApiMessageService:
            return m.id
        else:
            if m.reply_to is None:
                return 1
            else:
                if m.reply_to.reply_to_top_id is not None:
                    return m.reply_to.reply_to_top_id
                elif m.reply_to.reply_to_msg_id is not None:
                    return self.resolve_topic_id(self.get_message(m.reply_to.reply_to_msg_id))

    def get_message(self, message_id: int) -> Union[TgApiMessage, TgApiMessageService]:
        j = self.data.get(message_id)
        if j is None:
            return None
        if j['_'] == 'Message':
            return dataclass_from_dict(TgApiMessage, j)
        else:
            return dataclass_from_dict(TgApiMessageService, j)

    def get_latest_messages(self, date_gte: str) -> List[Union[TgApiMessage, TgApiMessageService]]:
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

    def get_latest_topic_messages(self, topic_id: int, since: str) -> List[Union[TgApiMessage, TgApiMessageService]]:
        return [m for m in (self.get_latest_messages(since)) if self.resolve_topic_id(m) == topic_id]
