import asyncio
import json

import click

from datatools.json.util import to_jsonisable
from datatools.tg import to_cache_folder, new_telegram_client
from datatools.tg.assistant.model.tg_model_factory import TgModelFactory


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
        cache_folder = to_cache_folder(session_slug)
        model_factory = TgModelFactory(cache_folder, client, since)
        channel_message_service = await model_factory.make_channel_message_service(channel_id)

        raw_messages = channel_message_service.channel_api_message_repository.get_latest_topic_raw_messages(topic_id, since)
        discussions = channel_message_service.make_latest_topic_discussion_forest(raw_messages)

        for m in discussions:
            print(json.dumps(to_jsonisable(m), ensure_ascii=False))
