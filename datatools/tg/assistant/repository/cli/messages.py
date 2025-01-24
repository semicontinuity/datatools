import click

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
def messages(session_slug: str, channel_id: int):
    repository = ChannelMessageRepository(cache_folder(session_slug), channel_id)
    repository.load()

    # for i in range(1, repository.get_max_id()):
    #     print(repository.get_message(i))

    messages = repository.get_latest_messages('2025-01-15')
    for message in messages:
        print(message)
