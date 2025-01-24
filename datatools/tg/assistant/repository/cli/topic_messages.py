import json

import click

from datatools.json.util import to_jsonisable
from datatools.tg import cache_folder
from datatools.tg.assistant.repository.channel_message_repository import ChannelMessageRepository


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
def topic_messages(session_slug: str, channel_id: int, topic_id: int, since: str):
    repository = ChannelMessageRepository(cache_folder(session_slug), channel_id)
    repository.load()

    messages = repository.get_latest_topic_messages(topic_id, since)
    for m in messages:
        print(json.dumps(to_jsonisable(m), ensure_ascii=False))
