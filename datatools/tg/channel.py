import asyncio
import json

import click
from telethon.tl.functions.channels import GetForumTopicsRequest

from datatools.json.util import to_jsonisable
from datatools.tg import new_telegram_client


async def do_dump_channel(client, channel_id: int):
    ch = await client.get_entity(channel_id)
    # full_channel = await client(GetFullChannelRequest(ch))
    # print(
    #     json.dumps(
    #         to_jsonisable(full_channel.to_dict()),
    #         ensure_ascii=False
    #     )
    # )

    t = await client(
        GetForumTopicsRequest(
            ch,
            offset_date=None,
            # offset_date=datetime.datetime(2025, 1, 19),
            offset_id=0,
            offset_topic=0,
            limit=1000,
            q=''
        )
    )
    print(
        json.dumps(
            to_jsonisable(t.to_dict()),
            ensure_ascii=False
        )
    )


async def dump_channel(telethon_session_slug: str, channel_id: int):
    async with await new_telegram_client(telethon_session_slug) as client:
        await do_dump_channel(client, channel_id)


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
def channel(session_slug: str, channel_id: int):
    asyncio.run(dump_channel(session_slug, channel_id))
