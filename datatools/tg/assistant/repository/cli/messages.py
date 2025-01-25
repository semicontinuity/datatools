import asyncio

import click

from datatools.tg import cache_folder, new_telegram_client
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
    "--since",
    type=str,
    help="Since",
)
def messages(session_slug: str, channel_id: int, since: str):
    asyncio.run(dump_messages(session_slug, channel_id, since))


async def dump_messages(session_slug: str, channel_id: int, since: str):
    async with await new_telegram_client(session_slug) as client:
        repository = ChannelMessageRepository(cache_folder(session_slug), client, channel_id)
        await repository.load()

        if since:
            for message in repository.get_latest_messages(since):
                print(message)
        else:
            for i in range(1, repository.get_max_id()):
                print(repository.get_message(i))
