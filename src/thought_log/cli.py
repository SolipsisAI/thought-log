import os
from pathlib import Path

import click

from thought_log.entry_handler import add_entry


@click.group()
def cli():
    pass


@cli.command()
@click.option("--oldest/--no-oldest", "-o", help="Oldest first")
@click.option(
    "--num_entries",
    "-n",
    default=5,
    help="Number of entries to show, Set to -1 to show all",
)
@click.option("--show-id/--no-show-id", "-i")
def show(oldest, num_entries, show_id):
    """Show entries"""
    from thought_log.entry_handler import show_entries

    click.echo_via_pager(
        show_entries(reverse=not oldest, num_entries=num_entries, show_id=show_id)
    )


@cli.command()
@click.option("--text", "-t")
@click.option("--filename", "-f", type=click.Path(exists=True))
def add(text, filename):
    """Add a new entry to the log"""
    from thought_log.entry_handler import write_entry

    if not any([text, filename]):
        print("Please supply text (--text/-t) or a path to a filename (--filename/-f)")
        exit(1)

    if all([text, filename]):
        print("Please either specify a file to import from or add text")
        exit(1)

    if text:
        write_entry(text)
    elif filename:
        add_entry(filename)


@cli.command()
@click.option("--import-filename", "-i", type=click.Path(exists=True))
def import_csv(import_filename):
    """Import a DayOne-exported CSV"""
    from thought_log.entry_handler import import_dayone_csv

    import_dayone_csv(import_filename)


@cli.command()
@click.option("--storage-dir", "-d", default=os.getenv("TL_STORAGE_DIR", None))
@click.option("--overwrite/--no-overwrite", default=False)
def configure(storage_dir, overwrite):
    """Configure settings"""
    from thought_log.utils import update_config, read_config

    config = read_config()

    if not storage_dir:
        storage_dir = click.prompt("Where do you want files to be stored? ")

    if "storage_dir" not in config or overwrite:
        config["storage_dir"] = storage_dir

    if not Path(storage_dir).exists():
        click.echo(f"{storage_dir} doesn't yet exist; created.")
        Path(storage_dir).mkdir(parents=True)

    update_config(config)


@cli.command()
def download():
    """Download models"""
    from thought_log.utils import download_models

    download_models()


@cli.command()
@click.option("--model-name", "-m")
@click.option("--tokenizer-name", "-t")
@click.option("--config-name", "-c")
@click.option("--classifier-name", "-cf")
@click.option("--pipeline/--no-pipeline", "-p")
@click.option("--max-length", default=1000)
def interact(
    model_name, tokenizer_name, config_name, classifier_name, pipeline, max_length
):
    """Use the chatbot interactively"""
    from thought_log.interact import interact

    interact(
        model_name, tokenizer_name, config_name, classifier_name, pipeline, max_length
    )
