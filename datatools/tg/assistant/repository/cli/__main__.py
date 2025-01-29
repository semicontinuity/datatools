import click

from datatools.tg.assistant.repository.cli.channel_ext_message_put import channel_ext_message_put
from datatools.tg.assistant.repository.cli.channel_raw_messages import channel_raw_messages
from datatools.tg.assistant.repository.cli.topic_raw_messages import topic_raw_messages


@click.group()
def main():
    pass


main.add_command(channel_ext_message_put)
main.add_command(channel_raw_messages)
main.add_command(topic_raw_messages)


if __name__ == "__main__":
    main()
