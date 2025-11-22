from abc import abstractmethod

from datatools.tg.api.tg_api_message import TgApiMessage
from datatools.tg.api.tg_api_message_service import TgApiMessageService
from datatools.tg.assistant.util.closeable import Closeable


class ChannelApiMessageRepository(Closeable):

    @abstractmethod
    def get_raw_message(self, message_id: int) -> None | TgApiMessage | TgApiMessageService:
        ...

    @abstractmethod
    def close(self):
        ...
