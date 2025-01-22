import os
import pathlib

from telethon import TelegramClient


def read_from(file_path: pathlib.Path) -> str:
    with open(str(file_path), 'r') as file:
        return file.read()


def cache_folder(telethon_session_slug: str) -> pathlib.Path:
    return pathlib.Path(os.environ['HOME']) / '.telethon' / telethon_session_slug


async def new_telegram_client(telethon_session_slug: str):
    folder = cache_folder(telethon_session_slug)
    api_id = int(read_from(folder / 'api_id').strip())
    api_hash = read_from(folder / 'api_hash').strip()
    session_file_name = str(folder / 'session.session')
    return TelegramClient(session_file_name, api_id, api_hash)
