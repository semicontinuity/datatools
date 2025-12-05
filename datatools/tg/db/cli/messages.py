import click

from datatools.tg.db.cli.messages_put import messages_put
from datatools.tg.db.cli.messages_get import messages_get


@click.group()
def messages():
    """Message management commands."""
    pass


messages.add_command(messages_put, name='put')
messages.add_command(messages_get, name='get')