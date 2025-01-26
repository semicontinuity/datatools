import click

from datatools.tg.assistant.service.cli.topic_discussions_unclassified import topic_discussions_unclassified
from datatools.tg.assistant.service.cli.topic_discussions_classified import topic_discussions_classified


@click.group()
def main():
    pass


main.add_command(topic_discussions_classified)
main.add_command(topic_discussions_unclassified)

if __name__ == "__main__":
    main()
