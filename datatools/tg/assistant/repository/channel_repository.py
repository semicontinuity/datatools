import pathlib
from typing import List

from datatools.tg.assistant.model.tg_channel import TgChannel
from datatools.tg.assistant.repository.channel_message_repository import ChannelMessageRepository


class ChannelRepository:

    def __init__(self, cache_folder: pathlib.Path, client) -> None:
        self.cache_folder = cache_folder
        self.folder = cache_folder / 'jsondb' / 'channels'
        self.client = client

    async def get_models(self) -> List[TgChannel]:
        channel_folder_names = [item.name for item in self.folder.iterdir() if item.is_dir()]
        channel_ids = [int(name) for name in channel_folder_names]
        dialogs = await self.client.get_dialogs()
        some_dialogs = [dialog for dialog in dialogs if dialog.id in channel_ids]
        return [TgChannel(id=d.id, name=d.name, repository=self.repo(d.id)) for d in some_dialogs]

    def repo(self, channel_id: int):
        r = ChannelMessageRepository(self.cache_folder, channel_id)
        r.load()
        return r
