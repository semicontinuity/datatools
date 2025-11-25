import click

from datatools.tg.api.cli.channel import channel
from datatools.tg.api.cli.channel_participants import channel_participants
from datatools.tg.api.cli.channels import channels
from datatools.tg.api.cli.dialogs import dialogs
from datatools.tg.api.cli.entity import entity
from datatools.tg.api.cli.groups import groups
from datatools.tg.api.cli.message import message
from datatools.tg.api.cli.messages import messages
from datatools.tg.api.cli.messagez import messagez
from datatools.tg.api.cli.topics import topics


@click.group()
def main():
    pass


main.add_command(channel)
main.add_command(channels)
main.add_command(channel_participants)
main.add_command(groups)
main.add_command(dialogs)
main.add_command(entity)
main.add_command(message)
main.add_command(messages)
main.add_command(messagez)
main.add_command(topics)


if __name__ == "__main__":
    main()
