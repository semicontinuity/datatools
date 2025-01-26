import asyncio
import json
import sys
from dataclasses import dataclass, asdict
from typing import Hashable

import click
from telethon.tl.functions.channels import GetFullChannelRequest

from datatools.json.util import to_jsonisable
from datatools.tg import new_telegram_client


@dataclass
class TgDialog:
    id: int
    name: str
    is_user: bool
    is_group: bool
    is_channel: bool
    megagroup: bool
    gigagroup: bool
    type: str
    # d: Hashable


async def do_dump_dialogs(client):
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:
            full_channel = await client(GetFullChannelRequest(dialog.entity))
            # print(full_channel, file=sys.stderr)

        print(
            json.dumps(
                asdict(
                    TgDialog(
                        id=dialog.id,
                        name=dialog.name,
                        is_user=dialog.is_user,
                        is_group=dialog.is_group,
                        is_channel=dialog.is_channel,
                        megagroup=dialog.entity.megagroup if dialog.is_channel else False,
                        gigagroup=dialog.entity.gigagroup if dialog.is_channel else False,
                        type=str(type(dialog.entity)),
                        # d=to_jsonisable(full_channel.to_dict()) if dialog.is_channel else {}
                    )
                ),
                ensure_ascii=False
            )
        )


async def dump_dialogs(telethon_session_slug: str):
    async with await new_telegram_client(telethon_session_slug) as client:
        await do_dump_dialogs(client)


@click.command()
@click.option(
    "--session-slug",
    required=True,
    help="Telethon session slug",
)
def dialogs(session_slug: str):
    asyncio.run(dump_dialogs(session_slug))
