import asyncio
import json

import click

from datatools.json.util import to_jsonisable
from datatools.tg import to_cache_folder, new_telegram_client
from datatools.tg.assistant.repository.channel_api_message_repository import ChannelApiMessageRepository


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
    required=True,
    help="Topic ID",
)
@click.option(
    "--since",
    type=str,
    required=True,
    help="Since",
)
def topic_raw_messages(session_slug: str, channel_id: int, topic_id: int, since: str):
    asyncio.run(dump_topic_raw_messages(session_slug, channel_id, topic_id, since))


async def dump_topic_raw_messages(session_slug: str, channel_id: int, topic_id: int, since: str):
    async with await new_telegram_client(session_slug) as client:
        repository = ChannelApiMessageRepository(to_cache_folder(session_slug), client, channel_id)
        await repository.load()

        messages = repository.get_latest_topic_raw_messages(topic_id, since)
        for m in messages:
            print(json.dumps(to_jsonisable(m), ensure_ascii=False))
