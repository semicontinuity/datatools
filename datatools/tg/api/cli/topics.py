import asyncio
import json

import click
from telethon.tl.functions.messages import GetForumTopicsRequest

from datatools.json.util import to_jsonisable
from datatools.tg import new_telegram_client


async def do_get_topics(client, channel_id: int):
    ch = await client.get_entity(channel_id)
    if not ch.forum:
        return []

    response = await client(
        GetForumTopicsRequest(
            ch,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=1000,
            q=None,
        )
    )
    return response.to_dict()['topics']


async def get_topics(telethon_session_slug: str, channel_id: int):
    async with await new_telegram_client(telethon_session_slug) as client:
        return await do_get_topics(client, channel_id)


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
    topic_list = asyncio.run(get_topics(session_slug, channel_id))

    for topic in topic_list:
        print(
            json.dumps(
                to_jsonisable(topic),
                ensure_ascii=False
            )
        )
