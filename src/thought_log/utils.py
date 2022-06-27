import csv
import json
import os
import re
import shutil
import tarfile
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests
from appdirs import user_data_dir, user_cache_dir, user_config_dir
from tqdm.auto import tqdm

from thought_log.res import urls

APP_NAME = "ThoughtLog"
APP_AUTHOR = "SolipsisAI"
ROOT_DIR = Path(__file__).parent.parent.parent.resolve()
DATA_DIR = ROOT_DIR.joinpath("data")
ZKID_DATE_FMT = "%Y%m%d%H%M%S"


def read_csv(filename: str) -> List[Dict]:
    with open(filename) as f:
        csv_data = csv.DictReader(f)
        return list(csv_data)


def read_json(filename: str, as_type=None) -> Dict:
    with open(filename, "r") as json_file:
        data = json.load(json_file)

        if as_type is not None:
            data = dict([(as_type(k), v) for k, v in data.items()])

        return data


def read_config():
    config_data = read_json(config_path().joinpath("config.json"))
    return config_data


def preprocess_text(text, classifier=None):
    """Prepend context label if classifier specified"""
    prefix = ""
    if classifier:
        context_label = classifier.classify(text, k=1)[0]
        prefix = f"{context_label} "
    return f"{prefix}{text}"


def postprocess_text(text):
    """Clean response text"""
    text = re.sub(r"^\w+\s", "", text)
    return re.sub(r"_comma_", ",", text)


def create_app_dirs():
    paths = [
        config_path(),
        cache_path(),
        app_data_path(),
        models_data_path(),
    ]
    for path in paths:
        if not path.exists():
            # Create user data directory
            path.mkdir(parents=True)


def update_config(data: Dict) -> Dict:
    config_filepath = config_path().joinpath("config.json")

    if config_filepath.exists():
        config_data = read_json(config_filepath)
        config_data.update(data)
    else:
        config_data = data

    with open(config_filepath, "w+") as fp:
        json.dump(config_data, fp, indent=4)

    return config_data


def config_path():
    return Path(user_config_dir(APP_NAME, APP_AUTHOR))


def cache_path():
    return Path(user_cache_dir(APP_NAME, APP_AUTHOR))


def app_data_path():
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def models_data_path():
    return app_data_path().joinpath("models")


def download_models():
    create_app_dirs()
    model_urls = urls.MODELS
    config_data = {}

    for name, url in model_urls.items():
        # Download the model
        dest_path = cache_path().joinpath(Path(url).name)

        if not dest_path.exists():
            download(url, dest_path=dest_path)

        # Extract the model files
        model_data_path = models_data_path().joinpath(name)

        if not model_data_path.exists():
            with tarfile.open(dest_path) as downloaded_model:
                downloaded_model.extractall(model_data_path)
            print(f"Extracted to {model_data_path}")
        else:
            print(f"{dest_path} already downloaded")

        # Set as model path in config
        extracted = list(filter(lambda x: x.is_dir(), model_data_path.glob("*")))

        config_data[f"{name}_path"] = str(extracted[0])

    update_config(config_data)


def download(url, dest_path):
    with requests.get(url, stream=True) as r:
        total_length = int(r.headers.get("Content-Length"))
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as f:
            with open(dest_path, "wb") as output:
                shutil.copyfileobj(f, output)


def zettelkasten_id(datetime_obj=None, include_seconds=True):
    """Generate an extended zettelksaten id"""
    if not datetime_obj:
        datetime_obj = datetime.now()

    fmt = ZKID_DATE_FMT if include_seconds else ZKID_DATE_FMT.replace("%S", "")

    return datetime_obj.strftime(fmt)


def snakecase(string):
    # From https://www.geeksforgeeks.org/python-program-to-convert-camel-case-string-to-snake-case/
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def to_datetime(string, fmt):
    if fmt == "isoformat":
        return datetime.fromisoformat(string)
    elif fmt == "zkid":
        return datetime.strptime(string, ZKID_DATE_FMT)
    else:
        return datetime.strptime(string, fmt)


def list_entries(entries_dir, reverse=False):
    return sorted(
        [int(f.stem) for f in Path(entries_dir).glob("*.txt")], reverse=reverse
    )


def window_size():
    return os.get_terminal_size()


def hline():
    return "-" * window_size().columns


def display_text(text):
    paragraphs = list(map(wrap_text, text.splitlines()))
    return "\n".join(paragraphs)


def wrap_text(text, padding: int = 5):
    lines = textwrap.wrap(text, width=window_size().columns - padding)
    return "\n".join(lines)
