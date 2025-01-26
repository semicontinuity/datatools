import sys

from datatools.tg.assistant.model.tg_user import TgUser
from datatools.util.dataclasses import dataclass_from_dict


class ChannelParticipantsRepository:
    data: dict[int, TgUser]

    def __init__(self, client, channel_id: int) -> None:
        self.client = client
        self.channel_id = channel_id
        self.data = dict()

    async def load(self):
        ch = await self.client.get_entity(self.channel_id)
        async for user in self.client.iter_participants(ch):
            d = user.to_dict()
            if d['_'] == 'User':
                self.data[d['id']] = dataclass_from_dict(TgUser, d)

    def get_user(self, user_id: int):
        print('Resolve ', user_id, file=sys.stderr)
        return self.data.get(user_id)
