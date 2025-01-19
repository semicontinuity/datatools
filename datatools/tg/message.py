import asyncio
import json

import click
from telethon.tl.functions.messages import GetMessagesRequest
from telethon.tl.types import InputMessageID

from datatools.json.util import to_jsonisable
from datatools.tg import new_telegram_client


async def do_dump_message(client, channel_id: int, message_id: int):
    ch = await client.get_entity(channel_id)

    # result = await client(GetMessagesRequest(
    #     id=[InputMessageID(message_id)]
    # ))
    #
    # json.dumps(
    #     result.to_dict(),
    #     ensure_ascii=False,
    # )

    async for message in client.iter_messages(channel_id, ids=[message_id]):
        # print(f"Message ID: {message.id}, Sender: {message.sender_id}, Text: {message.text}")
        print(
            json.dumps(
                to_jsonisable(message.to_dict()),
                ensure_ascii=False
            )
        )
        # print(
        #     message.to_dict()
        # )


async def dump_message(telethon_session_slug: str, channel_id: int, message_id: int):
    async with await new_telegram_client(telethon_session_slug) as client:
        await do_dump_message(client, channel_id, message_id)


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
    "--message-id",
    type=int,
    help="Message ID",
)
def message(session_slug: str, channel_id: int, message_id: int):
    asyncio.run(dump_message(session_slug, channel_id, message_id))
