import asyncio
import json
from dataclasses import dataclass, asdict

import click

from datatools.tg import new_telegram_client


@dataclass
class TgDialog:
    id: int
    name: str


async def do_dump_channels(client):
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:
            print(
                json.dumps(
                    asdict(
                        TgDialog(
                            id=dialog.id,
                            name=dialog.name,
                        )
                    ),
                    ensure_ascii=False
                )
            )


async def dump_channels(telethon_session_slug: str):
    async with await new_telegram_client(telethon_session_slug) as client:
        await do_dump_channels(client)


@click.command()
@click.option(
    "--session-slug",
    required=False,
    help="Telethon session slug (will use env var TELETHON_SESSION_SLUG if unspecified)",
)
def channels(session_slug: str | None):
    asyncio.run(dump_channels(session_slug))
