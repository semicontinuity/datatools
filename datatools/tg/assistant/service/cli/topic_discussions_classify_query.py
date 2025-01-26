import asyncio

import click

from datatools.tg import cache_folder, new_telegram_client
from datatools.tg.assistant.repository.channel_message_repository import ChannelMessageRepository
from datatools.tg.assistant.service.channel_message_service import ChannelMessageService
from datatools.tg.assistant.service.discussion_classifier import DiscussionClassifier


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
def topic_discussions_classify_query(session_slug: str, channel_id: int, topic_id: int, since: str):
    asyncio.run(dump_topic_discussions_classify_query(session_slug, channel_id, topic_id, since))


async def dump_topic_discussions_classify_query(session_slug: str, channel_id: int, topic_id: int, since: str):
    async with await new_telegram_client(session_slug) as client:
        repository = ChannelMessageRepository(cache_folder(session_slug), client, channel_id)
        await repository.load()

        service = ChannelMessageService(repository, channel_id)

        discussions = service.get_latest_topic_raw_discussions(topic_id, since)
        print(DiscussionClassifier().classify_query_discussions_part2(discussions))
