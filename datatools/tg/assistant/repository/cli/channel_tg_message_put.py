import json

import click

from datatools.tg import to_cache_folder
from datatools.tg.assistant.model.tg_message import TgMessage
from datatools.tg.assistant.repository.channel_ext_message_repository import ChannelExtMessageRepository
from datatools.util.dataclasses import dataclass_from_dict


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
    "--message",
    type=str,
    help="Message",
)
def channel_tg_message_put(session_slug: str, channel_id: int, message: str):
    _do_put(session_slug, channel_id, dataclass_from_dict(TgMessage, json.loads(message)))


def _do_put(session_slug: str, channel_id: int, message: TgMessage):
    repository = ChannelExtMessageRepository(to_cache_folder(session_slug), channel_id)
    repository.load_cached()
    repository.put_message(message)
    repository.save_cached()
