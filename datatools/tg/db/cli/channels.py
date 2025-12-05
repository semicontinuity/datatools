import click

from datatools.tg.db.cli.channels_import import channels_import
from datatools.tg.db.cli.channels_get import channels_get


@click.group()
def channels():
    """Channel management commands."""
    pass


channels.add_command(channels_import, name='put')
channels.add_command(channels_get, name='get')
