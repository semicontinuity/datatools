import asyncio
import json
from typing import Optional

import click

from datatools.json.util import to_jsonisable
from datatools.tg import new_telegram_client


async def do_dump_messages(client, channel_id: int, topic_id: Optional[int], min_id: Optional[int], max_id: Optional[int]):
    # ch = await client.get_entity(channel_id)

    # result = await client(GetHistoryRequest(
    #     peer=ch,
    #     offset_id=0,
    #     offset_date=None,
    #     add_offset=0,
    #     limit=10000,  # Number of messages to fetch
    #     max_id=0,
    #     min_id=0,
    #     hash=0,
    # ))
    #
    # message_list: List[Message] = result.messages

    if max_id or min_id:
        message_list = await client.get_messages(channel_id, min_id=min_id, max_id=max_id, reverse=True)
    else:
        message_list = await client.get_messages(channel_id, limit=100)

    for message in message_list:
        if topic_id:
            await dump_topic_message(message)

        else:
            print(json.dumps(to_jsonisable(message.to_dict()), ensure_ascii=False))


async def dump_topic_message(message):
    if message.reply_to:
        if message.reply_to.reply_to_top_id:
            msg_topic_id = message.reply_to.reply_to_top_id
        else:
            msg_topic_id = message.reply_to.reply_to_msg_id
    else:
        msg_topic_id = 1
    print(
        json.dumps(
            to_jsonisable(
                {
                    "id": message.id,
                    "data": message.date,
                    "topic": msg_topic_id,
                    # "reply_to_msg_id": message.reply_to.reply_to_msg_id if message.reply_to and message.reply_to.reply_to_msg_id else None,
                    # "reply_to_top_id": message.reply_to.reply_to_top_id if message.reply_to and message.reply_to.reply_to_top_id else None,
                    "message": message.messagez,
                }
            ),
            ensure_ascii=False
        )
    )
    # if message.reply_to and message.reply_to.reply_to_top_id == topic_id:
    #     print(
    #         json.dumps(
    #             {
    #                 "id": message.id,
    #                 "reply_to_msg_id": message.reply_to.reply_to_msg_id if message.reply_to and message.reply_to.reply_to_msg_id else None,
    #                 "message": message.message,
    #             },
    #             ensure_ascii=False
    #         )
    #     )


async def dump_messages(telethon_session_slug: str, channel_id: int, topic_id: Optional[int], min_id: Optional[int], max_id: Optional[int]):
    async with await new_telegram_client(telethon_session_slug) as client:
        await do_dump_messages(client, channel_id, topic_id, min_id, max_id)


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
@click.option(
    "--min-id",
    type=int,
    help="Min ID",
)
@click.option(
    "--max-id",
    type=int,
    help="Max ID",
)
def messages(session_slug: str, channel_id: int, topic_id: Optional[int], min_id: Optional[int], max_id: Optional[int]):
    asyncio.run(dump_messages(session_slug, channel_id, topic_id, min_id, max_id))
