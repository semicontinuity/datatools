import pathlib
from typing import List


class ChannelRepository:

    def __init__(self, cache_folder: pathlib.Path, client) -> None:
        self.cache_folder = cache_folder
        self.folder = cache_folder / 'jsondb' / 'channels'
        self.client = client

    async def get_dialogs(self) -> List:
        channel_folder_names = [item.name for item in self.folder.iterdir() if item.is_dir()]
        channel_ids = [int(name) for name in channel_folder_names]
        dialogs = await self.client.get_dialogs()
        return [dialog for dialog in dialogs if dialog.id in channel_ids]
