import asyncio
import json

import click

from datatools.json.util import to_jsonisable
from datatools.tg import cache_folder, new_telegram_client
from datatools.tg.assistant.repository.channel_api_message_repository import ChannelApiMessageRepository
from datatools.tg.assistant.repository.channel_participants_repository import ChannelParticipantsRepository
from datatools.tg.assistant.service.channel_message_service import ChannelMessageService


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
def topic_discussions_raw(session_slug: str, channel_id: int, topic_id: int, since: str):
    asyncio.run(dump_topic_discussions_raw(session_slug, channel_id, topic_id, since))


async def dump_topic_discussions_raw(session_slug: str, channel_id: int, topic_id: int, since: str):
    async with await new_telegram_client(session_slug) as client:
        channel_message_repository = ChannelApiMessageRepository(cache_folder(session_slug), client, channel_id)
        await channel_message_repository.load()

        channel_participants_repository = ChannelParticipantsRepository(client, channel_id)
        await channel_participants_repository.load()

        service = ChannelMessageService(channel_message_repository, channel_participants_repository, channel_id)

        messages = service.get_latest_topic_raw_discussions(topic_id, since)
        for m in messages:
            print(json.dumps(to_jsonisable(m), ensure_ascii=False))
