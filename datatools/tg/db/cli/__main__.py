import click
import logging

from datatools.tg.db.cli.channels import channels
from datatools.tg.db.cli.messages import messages
from datatools.tg.db.cli.users import users
from datatools.tg.db.cli.setup import init, status

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def main():
    """Telegram database CLI tools."""
    pass


main.add_command(channels)
main.add_command(messages)
main.add_command(users)
main.add_command(init)
main.add_command(status)


if __name__ == "__main__":
    main()
