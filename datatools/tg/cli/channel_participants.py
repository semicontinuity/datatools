import asyncio
import json

import click

from datatools.json.util import to_jsonisable
from datatools.tg import new_telegram_client


async def do_dump(client, channel_id: int):
    ch = await client.get_entity(channel_id)
    async for user in client.iter_participants(ch):
        print(
            json.dumps(
                to_jsonisable(user.to_dict()),
                ensure_ascii=False
            )
        )


async def dump(telethon_session_slug: str, channel_id: int):
    async with await new_telegram_client(telethon_session_slug) as client:
        await do_dump(client, channel_id)


@click.command()
@click.option(
    "--session-slug",
    required=True,
    help="Telethon session slug",
)
@click.option(
    "--channel-id",
    type=int,
    required=True,
    help="Channel ID",
)
def channel_participants(session_slug: str, channel_id: int):
    asyncio.run(dump(session_slug, channel_id))
