from pathlib import Path

import click

from thought_log.analyzer import DEFAULT_CLASSIFIERS
from thought_log.api import serve
from thought_log.config import INCLUDE_WEATHER, DEBUG
from thought_log.utils import unset_config


@click.group()
def cli():
    """Groups commands"""
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

    try:
        entries = show_entries(
            reverse=not oldest, num_entries=num_entries, show_id=show_id
        )
        click.echo_via_pager(entries)
    except ValueError as e:
        print(e)
        exit(1)


@cli.command()
@click.option(
    "--update",
    "-u",
    type=click.Choice(["emotion", "context", "sentiment"]),
    default=None,
)
def analyze(update):
    """Assign emotion classifications"""
    from thought_log.analyzer import analyze_entries

    if not update:
        update = DEFAULT_CLASSIFIERS

    analyze_entries(classifier_names=update)


@cli.command()
@click.argument("text")
@click.option("--weather/--no-weather", default=INCLUDE_WEATHER)
def add(text, weather):
    """Add entry from stdin"""
    from thought_log.entry_handler import write_entry

    write_entry(text, has_weather=weather)


@cli.command(name="import")
@click.argument("filename_or_directory", type=click.Path(exists=True))
def handle_import(filename_or_directory):
    """Import a file"""
    from thought_log.importer import filesystem as fs

    filepath = Path(filename_or_directory)

    if filepath.is_dir():
        print("Importing from directory")
        fs.import_from_directory(filepath)
    elif filepath.suffix == ".csv":
        print("Importing from csv")
        fs.import_from_csv(filepath)
    elif filepath.suffix == ".json":
        print("Importing from json")
        fs.import_from_json(filepath)
    else:
        print("Importing from file")
        fs.import_from_file(filepath)


@cli.command()
def import_gdoc():
    """Allow access to GDrive"""
    from thought_log.importer import google_drive

    drive = google_drive.init_drive()
    google_drive.walk(
        drive=drive, content_type="dir", process_fn=google_drive.import_from_file
    )


@cli.command(name="config")
@click.argument("action", type=click.Choice(["set", "unset", "show"]))
@click.option("--key", "-k")
@click.option("--value", "-v")
def handle_config(action, key, value):
    """Configure settings"""
    from thought_log.utils import get_config, set_config

    if action == "set":
        if not value or not key:
            click.echo("--key/-k and --value/-v required")
            exit(1)
        set_config(key, value)
    elif action == "unset":
        if not key:
            click("--key/-k required")
            exit(1)
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


@cli.command()
@click.option("--host", "-H", default="localhost")
@click.option("--port", "-P", default=8080)
@click.option("--debug/--no-debug", "-d", default=DEBUG)
def api(host, port, debug):
    """Serve API"""
    print(f"DEBUG: {debug}")
    serve(host=host, port=port, debug=debug)
