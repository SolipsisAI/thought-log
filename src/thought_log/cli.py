import click


@click.group()
def cli():
    pass


@cli.command()
@click.option("--message", "-m")
def add(message):
    print(f"Input: {message}")
