import click

from datatools.tg.cli.channel import channel
from datatools.tg.cli.channels import channels
from datatools.tg.cli.dialogs import dialogs
from datatools.tg.cli.groups import groups
from datatools.tg.cli.message import message
from datatools.tg.cli.messages import messages
from datatools.tg.cli.topics import topics


@click.group()
def main():
    pass


main.add_command(channel)
main.add_command(channels)
main.add_command(groups)
main.add_command(dialogs)
main.add_command(message)
main.add_command(messages)
main.add_command(topics)


if __name__ == "__main__":
    main()
