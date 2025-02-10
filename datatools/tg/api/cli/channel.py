import asyncio
import json

import click
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel
from telethon.tl.types.messages import ChatFull

from datatools.json.util import to_jsonisable
from datatools.tg import new_telegram_client


async def do_dump_channel(client, channel_id: int):
    ch = await client.get_entity(channel_id)
    full_channel: ChatFull = await client(GetFullChannelRequest(ch))

    channel = first_channel(full_channel)

    if channel:
        print(channel.forum)
        # print(
        #     json.dumps(
        #         to_jsonisable(channel.to_dict()),
        #         ensure_ascii=False
        #     )
        # )

    # t = await client(
    #     GetForumTopicsRequest(
    #         ch,
    #         offset_date=None,
    #         offset_date=datetime.datetime(2025, 1, 19),
            #: ChatFull offset_id=0,

    # full_channel


            # offset_topic=0,
            # limit=1000,
            # q=''
        # )
    # )
    # print(
    #     json.dumps(
    #         to_jsonisable(t.to_dict()),
    #         ensure_ascii=False
    #     )
    # )


def first_channel(full_channel: ChatFull) -> Channel|None:
    for chat in full_channel.chats:
        if type(chat) is Channel:
            return chat


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
