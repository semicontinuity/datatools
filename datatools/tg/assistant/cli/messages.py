import click

from datatools.tg import cache_folder
from datatools.tg.assistant.repository.channel_messages_repository import ChannelMessageRepository


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
def messages(session_slug: str, channel_id: int):
    ChannelMessageRepository(cache_folder(session_slug), channel_id).load()