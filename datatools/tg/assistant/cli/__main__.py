import click

from datatools.tg.assistant.cli.messages import messages


@click.group()
def main():
    pass


main.add_command(messages)


if __name__ == "__main__":
    main()
