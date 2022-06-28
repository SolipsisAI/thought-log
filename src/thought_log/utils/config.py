import json
from pathlib import Path
from typing import Dict, Union

import click

from .paths import config_path
from .io import read_json


def load_config():
    config_filepath = config_path().joinpath("config.json")

    if not config_path().exists():
        config_path().mkdir(parents=True)

    if not config_filepath.exists():
        update_config({})

    config_data = read_json(config_filepath)

    return config_data


def get_config(key: str = None):
    config = load_config()

    if not key:
        return "\n".join([f"{k}: {v}" for k, v in config.items()])

    return config.get(key)


def set_config(key, value):
    updated_config = update_config({key: value})
    return updated_config


def unset_config(key):
    config_data = load_config()
    if key in config_data:
        config_data.pop(key)
    save_config(config_data)


def update_config(data: Dict) -> Dict:
    config_filepath = config_path().joinpath("config.json")

    if config_filepath.exists():
        config_data = read_json(config_filepath)
        config_data.update(data)
    else:
        config_data = data

    save_config(config_data)

    return config_data


def save_config(config_data):
    config_filepath = config_path().joinpath("config.json")

    with open(config_filepath, "w+") as fp:
        json.dump(config_data, fp, indent=4)


def configure_storage(storage_dir: Union[str, Path]):
    config = load_config()

    if not storage_dir:
        storage_dir = click.prompt("Where do you want files to be stored? ")

    if "storage_dir" not in config:
        config["storage_dir"] = storage_dir

    if not Path(storage_dir).exists():
        click.echo(f"{storage_dir} doesn't yet exist; created.")
        Path(storage_dir).mkdir(parents=True)

    update_config(config)
