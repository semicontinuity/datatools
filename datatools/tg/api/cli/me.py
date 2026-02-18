import asyncio

import click

from datatools.tg import new_telegram_client


async def get_me(telethon_session_slug: str):
    async with await new_telegram_client(telethon_session_slug) as client:
        return await client.get_me()


@click.command()
@click.option(
    "--session-slug",
    required=True,
    help="Telethon session slug",
)
def me(session_slug: str):
    print(asyncio.run(get_me(session_slug)))
