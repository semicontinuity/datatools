import asyncio
import json
from typing import Optional, List

import click
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.patched import Message

from datatools.json.util import to_jsonisable
from datatools.tg import new_telegram_client


async def do_dump_messages(client, channel_id: int, topic_id: Optional[int]):
    ch = await client.get_entity(channel_id)

    result = await client(GetHistoryRequest(
        peer=ch,
        offset_id=0,
        offset_date=None,
        add_offset=0,
        limit=10000,  # Number of messages to fetch
        max_id=0,
        min_id=0,
        hash=0,
    ))

    messages: List[Message] = result.messages
    for message in messages:
        if topic_id:
        # topic = message.reply_to and message.reply_to.forum_topic
        # topic1 = message.reply_to.reply_to_top_id if message.reply_to and message.reply_to.forum_topic else None
        # if topic

        # print(topic, topic1, message.reply message.date, message.message)

            if message.reply_to and message.reply_to.reply_to_top_id == topic_id:
                print(
                    json.dumps(
                        {
                            "id": message.id,
                            "reply_to_msg_id": message.reply_to.reply_to_msg_id if message.reply_to and message.reply_to.reply_to_msg_id else None,
                            "message": message.message,
                        },
                        ensure_ascii=False
                    )
                )
        else:
            print(json.dumps(to_jsonisable(message.to_dict()), ensure_ascii=False))


async def dump_messages(telethon_session_slug: str, channel_id: int, topic_id: Optional[int]):
    async with await new_telegram_client(telethon_session_slug) as client:
        await do_dump_messages(client, channel_id, topic_id)


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
    "--topic-id",
    type=int,
    help="Topic ID",
)
def messages(session_slug: str, channel_id: int, topic_id: Optional[int]):
    asyncio.run(dump_messages(session_slug, channel_id, topic_id))
