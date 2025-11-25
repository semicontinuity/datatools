import asyncio
import json
from datetime import datetime

import click

from datatools.json.util import to_jsonisable
from datatools.tg import new_telegram_client


async def do_get_messages(client, channel_id: int, offset_date: str | None, limit: int):
    result = []

    if offset_date:
        offset_date = datetime.strptime(offset_date, '%Y-%m-%d')

    async for message in client.iter_messages(channel_id, offset_date=offset_date, limit=limit):
        result.append(message)
    return result


async def get_messages(telethon_session_slug: str, channel_id: int, offset_date: str | None, limit: int):
    async with await new_telegram_client(telethon_session_slug) as client:
        return await do_get_messages(client, channel_id, offset_date, limit)


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
@click.option(
    "--offset-date",
    type=str,
    help="Offset date",
)
@click.option(
    "--limit",
    type=int,
    default=100,
    help="Limit",
)
def messagez(session_slug: str, channel_id: int, offset_date: str | None, limit: int):
    r = asyncio.run(get_messages(session_slug, channel_id, offset_date, limit))

    for message in r:
        print(
            json.dumps(
                to_jsonisable(message.to_dict()),
                ensure_ascii=False
            )
        )
