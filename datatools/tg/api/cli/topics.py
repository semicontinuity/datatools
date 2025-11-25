import asyncio
import json

import click
# from telethon.tl.functions.channels import GetForumTopicsRequest
from telethon.tl.functions.messages import GetForumTopicsRequest

from datatools.json.util import to_jsonisable
from datatools.tg import new_telegram_client


async def do_dump_topics(client, channel_id: int):
    ch = await client.get_entity(channel_id)

    response = await client(
        GetForumTopicsRequest(
            ch,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=1000,
            q=''
        )
    )

    for topic in response.to_dict()['topics']:
        print(
            json.dumps(
                to_jsonisable(topic),
                ensure_ascii=False
            )
        )


async def dump_topics(telethon_session_slug: str, channel_id: int):
    async with await new_telegram_client(telethon_session_slug) as client:
        await do_dump_topics(client, channel_id)


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
def topics(session_slug: str, channel_id: int):
    asyncio.run(dump_topics(session_slug, channel_id))
