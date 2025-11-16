import asyncio
import sys

import click

from datatools.tg import to_cache_folder, new_telegram_client, json_dump
from datatools.tg.assistant.model.tg_model_factory import TgModelFactory
from datatools.tg.assistant.service.discussion_classifier import DiscussionClassifier
from yndx.llm.factory import llm


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
@click.option(
    "--llm-provider",
    type=str,
    default="gradio",
    help="LLM Provider",
)
def topic_discussions_classified(session_slug: str, channel_id: int, topic_id: int, since: str, llm_provider: str):
    asyncio.run(dump_topic_discussions_classified(session_slug, channel_id, topic_id, since, llm_provider))


async def dump_topic_discussions_classified(session_slug: str, channel_id: int, topic_id: int, since: str, llm_provider):
    async with await new_telegram_client(session_slug) as client:
        cache_folder = to_cache_folder(session_slug)
        model_factory = TgModelFactory(cache_folder, client, since)
        channel_message_service = await model_factory.make_channel_message_service(channel_id)

        raw_messages = channel_message_service.channel_api_message_repository.get_latest_topic_raw_messages(topic_id, since)
        print(f'Fetched {len(raw_messages)} messages in channel {channel_id}, topic {topic_id} since {since}', file=sys.stderr)
        discussions = channel_message_service.make_latest_topic_discussion_forest(raw_messages)
        print(f'Converted to {len(discussions)} discussions in channel {channel_id}, topic {topic_id}', file=sys.stderr)

        print(json_dump(DiscussionClassifier(llm(llm_provider)).classify(discussions)))

        channel_message_service.channel_ext_message_repository.save_cached()
