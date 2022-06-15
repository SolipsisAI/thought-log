import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument("text")
def add(text):
    print(f"Input: {text}")
