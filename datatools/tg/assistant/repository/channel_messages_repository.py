import pathlib
from typing import List


class ChannelMessageRepository:
    file: pathlib.Path
    data: List

    def __init__(self, cache_folder: pathlib.Path, channel_id: int) -> None:
        self.file = cache_folder / 'jsondb' / 'channels' / str(channel_id) / 'messages.jsonl'

    def load(self):
        with open(self.file, 'r') as file:
            for line in file:
                print(line.strip())
