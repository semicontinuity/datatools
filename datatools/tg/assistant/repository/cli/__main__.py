import click

from datatools.tg.assistant.repository.cli.channel_raw_messages import channel_raw_messages
from datatools.tg.assistant.repository.cli.topic_raw_discussions import topic_raw_discussions
from datatools.tg.assistant.repository.cli.topic_raw_messages import topic_raw_messages


@click.group()
def main():
    pass


main.add_command(channel_raw_messages)
main.add_command(topic_raw_messages)
main.add_command(topic_raw_discussions)


if __name__ == "__main__":
    main()
