import click

from datatools.tg.channels import channels


@click.group()
def main():
    pass


main.add_command(channels)


if __name__ == "__main__":
    main()
