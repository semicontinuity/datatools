import asyncio
import json
from dataclasses import dataclass, asdict

import click

from datatools.tg import new_telegram_client


@dataclass
class TgGroup:
    id: int
    name: str


async def do_dump_groups(client):
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            print(
                json.dumps(
                    asdict(
                        TgGroup(
                            id=dialog.id,
                            name=dialog.name,
                        )
                    ),
                    ensure_ascii=False
                )
            )


async def dump_groups(telethon_session_slug: str):
    async with await new_telegram_client(telethon_session_slug) as client:
        await do_dump_groups(client)


@click.command()
@click.option(
    "--session-slug",
    required=True,
    help="Telethon session slug",
)
def groups(session_slug: str):
    asyncio.run(dump_groups(session_slug))
