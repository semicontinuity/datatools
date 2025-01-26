from datatools.tg.assistant.model.tg_user import TgUser
from datatools.util.dataclasses import dataclass_from_dict


class ChannelParticipantsRepository:

    def __init__(self, client, channel_id: int) -> None:
        self.client = client
        self.channel_id = channel_id

    async def load(self) -> dict[int, TgUser]:
        ch = await self.client.get_entity(self.channel_id)
        res: dict[int, TgUser] = dict()
        async for user in self.client.iter_participants(ch):
            d = user.to_dict()
            if d['_'] == 'User':
                d['id'] = dataclass_from_dict(TgUser, d)
        return res
