import os
import re
import shutil
import tarfile
import textwrap
from collections import Counter
from datetime import date, datetime, time
from pathlib import Path
from typing import Union

import requests
from huggingface_hub import snapshot_download
from tqdm.auto import tqdm

from thought_log.res import urls

from .config import update_config
from .paths import cache_path, create_app_dirs, models_data_path

APP_NAME = "ThoughtLog"
APP_AUTHOR = "SolipsisAI"
ROOT_DIR = Path(__file__).parent.parent.parent.resolve()
DATA_DIR = ROOT_DIR.joinpath("data")
ZKID_DATE_FMT = "%Y%m%d%H%M%S"
DEBUG = os.getenv("DEBUG", False)


def preprocess_text(text, classifier=None):
    """Prepend context label if classifier specified"""
    prefix = ""
    if classifier:
        text = text.strip()
        context_label = classifier.classify(text, k=1)[0]

        if DEBUG:
            print(context_label)

        prefix = f"{context_label} "
    return f"{prefix}{text}"


def postprocess_text(text):
    """Clean response text"""
    text = re.sub(r"^\w+\s", "", text)
    return re.sub(r"_comma_", ",", text)


def download_models():
    create_app_dirs()
    model_urls = urls.MODELS
    config_data = {}

    for name, info in model_urls.items():
        url = info["url"]
        source = info["source"]

        if source == "huggingface":
            config_data[f"{name}_path"] = url
            download(url, source=source)
            # Skip extraction since huggingface handles this
            continue

        # Download the model
        dest_path = cache_path().joinpath(Path(url).name)

        if not dest_path.exists():
            download(url, source=source, dest_path=dest_path)

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


def download(url, source, dest_path=None, revision="main"):
    if source == "huggingface":
        snapshot_download(repo_id=url, revision=revision)
        return

    if not dest_path:
        raise ValueError("dest_path is not set, please specify")

    with requests.get(url, stream=True) as r:
        total_length = int(r.headers.get("Content-Length"))
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as f:
            with open(dest_path, "wb") as output:
                shutil.copyfileobj(f, output)


def zettelkasten_id(datetime_obj=None, include_seconds=True) -> int:
    """Generate an extended zettelksaten id"""
    if not datetime_obj:
        datetime_obj = datetime.now()

    fmt = ZKID_DATE_FMT if include_seconds else ZKID_DATE_FMT.replace("%S", "")

    return int(make_datetime(datetime_obj).strftime(fmt))


def snakecase(string):
    # From https://www.geeksforgeeks.org/python-program-to-convert-camel-case-string-to-snake-case/
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def make_datetime(obj: Union[str, datetime], fmt: str = None):
    if isinstance(obj, datetime):
        return obj

    if fmt and isinstance(obj, str):
        if fmt == "isoformat":
            return datetime.fromisoformat(obj[:-1])
        return datetime.strptime(obj, fmt)

    return find_datetime(obj)


def list_entries(entries_dir, reverse=False, num_entries=-1):
    entry_ids = sorted(
        [int(f.stem.split(".")[0]) for f in Path(entries_dir).glob("*.json")],
        reverse=reverse,
    )
    return entry_ids if num_entries < 0 else entry_ids[:num_entries]


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


def sanitize_text(text):
    """Sanitize JSON-encoded text"""
    return text.replace("\\", "")


def flatten(original_list):
    # https://appdividend.com/2022/06/17/how-to-flatten-list-in-python/
    return [element for sublist in original_list for element in sublist]


def frequency(labels, key: str):
    get_label = lambda x: x[key][0]["label"] if "score" in x[key][0] else x[key][0]
    return Counter(list(map(get_label, labels)))


def get_top_labels(label_frequency: Counter, k: int = 1):
    """Get top labels. If there is a tie, show all"""
    counts = sorted(set(list(label_frequency.values())), reverse=True)
    top_counts = counts[:k] if k > 0 else counts
    is_top = lambda l: l[1] in top_counts

    top_labels = list(
        map(
            lambda label: label[0],
            filter(is_top, label_frequency.items()),
        )
    )

    return top_labels


def find_datetime(input_string: str):
    """Extract the first datetime object from an input string"""
    if not input_string:
        return

    date_obj = find_date(input_string)
    time_obj = find_time(input_string)

    if not date_obj and not time_obj:
        return

    if not date_obj:
        d = datetime.today()
        date_obj = date(d.year, d.month, d.day)

    if not time_obj:
        time_obj = time(0, 0, 0)

    datetime_obj = datetime.combine(date_obj, time_obj)

    return datetime_obj


def find_date(input_string):
    if isinstance(input_string, date):
        return input_string

    if not isinstance(input_string, str):
        return

    date_pattern = (
        "(\d{4})(?:\/|-|\.)(0[1-9]|1[0-2])(?:\/|-|\.)(0[1-9]|[12][0-9]|3[01])"
    )
    date_matches = re.findall(date_pattern, input_string)

    if not date_matches:
        return

    year, month, day = date_matches[0]
    return date(int(year), int(month), int(day))


def find_time(input_string):
    if isinstance(input_string, time):
        return input_string

    if not isinstance(input_string, str):
        return

    time_pattern = (
        "(0[1-2]|[0-2][0-9])(?:\:)(0[1-9]|[0-5][0-9])(?:\:)(0[1-9]|[0-5][0-9])"
    )
    time_matches = re.findall(time_pattern, input_string)

    if not time_matches:
        return

    hour, minute, second = time_matches[0]
    return time(int(hour), int(minute), int(second))


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
