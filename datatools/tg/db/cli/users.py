import click

from datatools.tg.db.cli.users_put import users_put
from datatools.tg.db.cli.users_get import users_get


@click.group()
def users():
    """User management commands."""
    pass


users.add_command(users_put, name='put')
users.add_command(users_get, name='get')