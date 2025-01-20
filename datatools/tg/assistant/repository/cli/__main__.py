import click

from datatools.tg.assistant.repository.cli.messages import messages
from datatools.tg.assistant.repository.cli.topic_messages import topic_messages


@click.group()
def main():
    pass


main.add_command(messages)
main.add_command(topic_messages)


if __name__ == "__main__":
    main()
