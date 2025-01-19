import os
import pathlib

from telethon import TelegramClient


def read_from(file_path: pathlib.Path) -> str:
    with open(str(file_path), 'r') as file:
        return file.read()


async def new_telegram_client(telethon_session_slug):
    api_id = int(read_from(pathlib.Path(os.environ['HOME']) / '.telethon' / telethon_session_slug / 'api_id').strip())
    api_hash = read_from(pathlib.Path(os.environ['HOME']) / '.telethon' / telethon_session_slug / 'api_hash').strip()
    session_file_name = str(pathlib.Path(os.environ['HOME']) / '.telethon' / telethon_session_slug / 'session.session')
    telegram_client = TelegramClient(session_file_name, api_id, api_hash)
    return telegram_client
