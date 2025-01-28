import asyncio

import click

from datatools.tg import to_cache_folder, new_telegram_client
from datatools.tg.assistant.model.tg_model_factory import TgModelFactory
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
        cache_folder = to_cache_folder(session_slug)
        model_factory = TgModelFactory(cache_folder, client)
        channel_message_service = await model_factory.make_channel_message_service(channel_id)

        discussions = channel_message_service.get_latest_topic_raw_discussions(topic_id, since)
        classifier = DiscussionClassifier()

        flat_discussions = classifier.flat_discussions(discussions)
        print(classifier.classify_discussions_query_data(flat_discussions))
