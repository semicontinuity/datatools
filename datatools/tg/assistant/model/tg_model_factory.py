from telethon import TelegramClient

from datatools.tg.assistant.model.tg_root_objects import TgRootObjects
from datatools.tg.assistant.service.channel_message_service import ChannelMessageService


class TgModelFactory:
    client: TelegramClient

    def __init__(self, client: TelegramClient) -> None:
        self.client = client

    async def make_tg_root_objects(self) -> TgRootObjects:
        ...

    async def make_channel_message_service(self, channel_id: int) -> ChannelMessageService:
        ...

    def close(self):
        ...
