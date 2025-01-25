import json
import pathlib
import sys
from typing import List, Dict, Union

from datatools.json.util import to_jsonisable
from datatools.tg.assistant.api.tg_api_message import TgApiMessage
from datatools.tg.assistant.api.tg_api_message_service import TgApiMessageService
from datatools.util.dataclasses import dataclass_from_dict

CACHE_FILE_SIZE = 256


class ChannelMessageRepository:
    files_folder: pathlib.Path
    data: Dict[int, Dict]
    cache_max_id: int
    max_id: int
    channel_id: int

    def __init__(self, cache_folder: pathlib.Path, client, channel_id: int) -> None:
        self.files_folder = cache_folder / 'jsondb' / 'channels' / str(channel_id)
        self.client = client
        self.channel_id = channel_id
        self.cache_max_id = 0
        self.max_id = 0
        self.data = {}

    async def load(self):
        self.load_cache()
        await self.load_recent_messages()

    async def load_recent_messages(self):
        print(f'Loading recent messages for channel {self.channel_id}', file=sys.stderr)
        recent_messages = await self.client.get_messages(self.channel_id, min_id=self.max_id, max_id=None, reverse=True)
        for m in recent_messages:
            s = json.dumps(to_jsonisable(m.to_dict()), ensure_ascii=False)
            j = json.loads(s)
            message_id = j['id']
            self.data[message_id] = j
            self.max_id = max(self.max_id, message_id)

    def load_cache(self):
        print(f'Loading cache for channel {self.channel_id}', file=sys.stderr)

        i = 0
        while True:
            path = self.files_folder / ("%08x" % i)
            if not path.exists():
                break

            with open(path, 'r') as file:
                for line in file:
                    j = json.loads(line)
                    message_id = j['id']
                    self.data[message_id] = j
                    self.cache_max_id = max(self.cache_max_id, message_id)

            i += CACHE_FILE_SIZE

        self.max_id = self.cache_max_id

    def save_cache(self):
        print(f'Saving cache for channel {self.channel_id}', file=sys.stderr)

        i = self.cache_max_id // CACHE_FILE_SIZE * CACHE_FILE_SIZE
        while i <= self.max_id:
            path = self.files_folder / ("%08x" % i)
            with open(path, 'w') as file:
                for k in range(i, i + CACHE_FILE_SIZE):
                    j = self.data.get(k)
                    if j:
                        print(json.dumps(j, ensure_ascii=False), file=file)
            i += CACHE_FILE_SIZE

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

    def get_message(self, message_id: int) -> Union[None, TgApiMessage, TgApiMessageService]:
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
