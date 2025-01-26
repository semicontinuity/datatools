import click

from datatools.tg.assistant.api.cli.channel import channel
from datatools.tg.assistant.api.cli.channel_participants import channel_participants
from datatools.tg.assistant.api.cli.channels import channels
from datatools.tg.assistant.api.cli.dialogs import dialogs
from datatools.tg.assistant.api.cli.groups import groups
from datatools.tg.assistant.api.cli.message import message
from datatools.tg.assistant.api.cli.messages import messages
from datatools.tg.assistant.api.cli.topics import topics


@click.group()
def main():
    pass


main.add_command(channel)
main.add_command(channels)
main.add_command(channel_participants)
main.add_command(groups)
main.add_command(dialogs)
main.add_command(message)
main.add_command(messages)
main.add_command(topics)


if __name__ == "__main__":
    main()
