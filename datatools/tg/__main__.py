import click

from datatools.tg.channel import channel
from datatools.tg.channels import channels
from datatools.tg.dialogs import dialogs
from datatools.tg.groups import groups
from datatools.tg.messages import messages
from datatools.tg.topics import topics


@click.group()
def main():
    pass


main.add_command(channel)
main.add_command(channels)
main.add_command(groups)
main.add_command(dialogs)
main.add_command(messages)
main.add_command(topics)


if __name__ == "__main__":
    main()
