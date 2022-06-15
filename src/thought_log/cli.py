import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument("text")
def add(text):
    from thought_log.utils import ROOT_DIR, DATA_DIR
    print(f"Input: {text}|{ROOT_DIR} {DATA_DIR}")
