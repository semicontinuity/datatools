import asyncio

import click

from datatools.tg import new_telegram_client


async def get_entity(telethon_session_slug: str, entity_id: int):
    async with await new_telegram_client(telethon_session_slug) as client:
        return await client.get_entity(entity_id)


@click.command()
@click.option(
    "--session-slug",
    required=True,
    help="Telethon session slug",
)
@click.option(
    "--entity-id",
    type=int,
    required=True,
    help="Entity ID",
)
def entity(session_slug: str, entity_id: int):
    print(asyncio.run(get_entity(session_slug, entity_id)))
