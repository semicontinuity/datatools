import json
import pathlib
import sys

from sortedcontainers import SortedDict

from datatools.json.util import to_jsonisable
from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.util.dataclasses import dataclass_from_dict

CACHE_FILE_SIZE = 256
CACHE_FILE_PREFIX = 'msg_'


class ChannelExtMessageRepository:
    files_folder: pathlib.Path
    buckets: SortedDict[int, SortedDict[int, TgMessage]]
    channel_id: int

    def __init__(self, cache_folder: pathlib.Path, channel_id: int) -> None:
        self.files_folder = cache_folder / 'jsondb' / 'channels' / str(channel_id)
        self.channel_id = channel_id
        self.buckets = SortedDict()

    def file_name(self, i):
        return f"{CACHE_FILE_PREFIX}%08x" % i

    def get_message(self, message_id: int) -> TgMessage:
        return self._bucket(message_id).get(message_id)

    def put_message(self, message: TgMessage):
        self._bucket(message.id)[message.id] = message

    def _bucket(self, message_id: int):
        i = message_id // CACHE_FILE_SIZE
        bucket = self.buckets.get(i)
        if bucket is None:
            bucket = SortedDict()
            self.buckets[i] = bucket
        return bucket

    def load_cached(self):
        print(f'Loading cache for channel {self.channel_id}', file=sys.stderr)

        for x in self.files_folder.iterdir():
            if x.is_file() and x.name.startswith(CACHE_FILE_PREFIX):
                with open(x, 'r') as file:
                    for line in file:
                        self.put_message(dataclass_from_dict(TgMessage, json.loads(line)))

    def save_cached(self):
        print(f'Saving cache for channel {self.channel_id}', file=sys.stderr)

        for k, bucket in self.buckets.items():
            path = self.files_folder / self.file_name(k)
            with open(path, 'w') as file:
                for m in bucket.values():
                    print(json.dumps(to_jsonisable(m), ensure_ascii=False), file=file)
