import click

from datatools.tg.assistant.service.cli.topic_discussions_classified import topic_discussions_classified
from datatools.tg.assistant.service.cli.topic_discussions_classify_query import topic_discussions_classify_query
from datatools.tg.assistant.service.cli.topic_discussions_raw import topic_discussions_raw


@click.group()
def main():
    pass


main.add_command(topic_discussions_classified)
main.add_command(topic_discussions_classify_query)
main.add_command(topic_discussions_raw)

if __name__ == "__main__":
    main()
