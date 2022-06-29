from pathlib import Path

import click

from thought_log.entry_handler import import_from_directory
from thought_log.utils import unset_config


@click.group()
def cli():
    pass


@cli.command()
def google():
    """Allow access to GDrive"""
    from thought_log.importer import google_drive

    postbox = google_drive.list_dirs("Postbox")


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

    try:
        entries = show_entries(
            reverse=not oldest, num_entries=num_entries, show_id=show_id
        )
        click.echo_via_pager(entries)
    except ValueError as e:
        print(e)
        exit(1)


@cli.command()
def analyze():
    """Assign emotion classifications"""
    from thought_log.entry_handler import classify_entries

    classify_entries()


@cli.command()
@click.argument("text")
def add(text):
    """Add entry from stdin"""
    from thought_log.entry_handler import write_entry

    write_entry(text)


@cli.command(name="import")
@click.argument("filename_or_directory", type=click.Path(exists=True))
def handle_import(filename_or_directory):
    """Import a file"""
    from thought_log.entry_handler import import_from_csv, import_from_file

    filepath = Path(filename_or_directory)

    if filepath.is_dir():
        print("Importing from directory")
        import_from_directory(filepath)
    elif filepath.suffix == ".csv":
        print("Importing from csv")
        import_from_csv(filepath)
    else:
        print("Import from file")
        import_from_file(filepath)


@cli.command(name="config")
@click.argument("action", type=click.Choice(["set", "unset", "show"]))
@click.option("--key", "-k")
@click.option("--value", "-v")
def handle_config(action, key, value):
    """Configure settings"""
    from thought_log.utils import get_config, set_config

    if action == "set":
        set_config(key, value)
    elif action == "unset":
        unset_config(key)
    else:
        click.echo(f"{get_config(key)}")


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
