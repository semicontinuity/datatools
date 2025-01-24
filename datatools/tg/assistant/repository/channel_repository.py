import pathlib
from typing import List

from datatools.tg.assistant.model.tg_channel import TgChannel


class ChannelRepository:

    def __init__(self, cache_folder: pathlib.Path, client) -> None:
        self.folder = cache_folder / 'jsondb' / 'channels'
        self.client = client

    async def load(self) -> None:
        channel_folder_names = [item.name for item in self.folder.iterdir() if item.is_dir()]
        channel_ids = [int(name) for name in channel_folder_names]
        dialogs = await self.client.get_dialogs()
        self.dialogs = [dialog for dialog in dialogs if dialog.id in channel_ids]

    def models(self) -> List[TgChannel]:
        return [TgChannel(id=d.id, name=d.name) for d in self.dialogs]
