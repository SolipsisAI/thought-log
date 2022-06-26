import os
from pathlib import Path

import click


@click.group()
def cli():
    pass


@cli.command()
@click.option("--text", "-t")
@click.option("--import_filename", "-i")
def add(text, import_filename):
    """Add a new entry to the log"""
    from thought_log.entry_handler import write_entry, classify_entry

    if not any([text, import_filename]):
        raise ValueError("Please supply text or a path to a filename")

    metadata = {"tags": classify_entry(text)}
    write_entry(text, metadata)


@cli.command()
@click.option("--storage_dir", "-d", default=os.getenv("TL_STORAGE_DIR", None))
@click.option("--overwrite/--no_overwrite", default=False)
def configure(storage_dir, overwrite):
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
@click.option("--model_name", "-m")
@click.option("--tokenizer_name", "-t")
@click.option("--config_name", "-c")
@click.option("--classifier_name", "-cf")
@click.option("--pipeline/--no-pipeline", "-p")
@click.option("--max_length", default=1000)
def interact(
    model_name, tokenizer_name, config_name, classifier_name, pipeline, max_length
):
    """Use the chatbot interactively"""
    from thought_log.interact import interact

    interact(
        model_name, tokenizer_name, config_name, classifier_name, pipeline, max_length
    )
