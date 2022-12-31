from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Dict, Union

import frontmatter
from tqdm.auto import tqdm

from thought_log.config import STORAGE_DIR, DEBUG
from thought_log.models import Note, Notebook
from thought_log.utils import (
    generate_uuid,
    generate_hash_from_string,
    get_filetype,
    make_datetime,
    read_csv,
    read_json,
    read_file,
    timestamp,
)

SUPPORTED_FILETYPES = ["text/plain", "text/markdown", "text/csv", "text/json"]

READERS = {
    "text/csv": read_csv,
    "text/json": read_json,
    "text/plain": read_file,
}


def import_data(fp: Union[str, Path, TextIOWrapper], filetype=None):
    if not filetype:
        filetype = get_filetype(fp)

    if filetype not in SUPPORTED_FILETYPES:
        return

    data = READERS[filetype](fp)

    IMPORTERS[filetype](data)


def _import_item(item):
    notebook = item.pop("notebook", 1)  # default notebook
    uuid = item.pop("uuid", generate_uuid())
    file_hash = item.pop("file_hash", generate_hash_from_string(item.get("text", "")))

    item["notebook"] = notebook
    item["uuid"] = uuid
    item["file_hash"] = file_hash
    date = item.pop("date", None)
    item["created"] = timestamp(make_datetime(date))

    Note(item).save()


def import_csv(data):
    for row in data:
        _import_item(row)


def import_json(data):
    _import_item(data)


def import_file(data):
    _import_item(data)


IMPORTERS = {
    "text/csv": import_csv,
    "text/json": import_json,
    "text/plain": import_file,
}
