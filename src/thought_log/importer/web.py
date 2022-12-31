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
    read_zipfile,
    timestamp,
)

SUPPORTED_FILETYPES = [
    "application/zip",
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/json",
]

READERS = {
    "text/csv": read_csv,
    "application/json": read_json,
    "text/plain": read_file,
    "application/zip": read_zipfile,
}


def import_data(fp, filetype=None):
    if not filetype:
        filetype = get_filetype(fp)

    if filetype not in SUPPORTED_FILETYPES:
        return

    if filetype != "application/zip":
        fp = TextIOWrapper(fp)

    data = READERS[filetype](fp)

    return IMPORTERS[filetype](data)


def import_csv(data):
    skipped = 0
    success = 0

    for item in data:
        if not item.get("text", None):
            skipped += 1
            continue

        notebook = item.pop("notebook", 1)  # default notebook
        uuid = item.pop("uuid", generate_uuid())
        file_hash = item.pop(
            "file_hash", generate_hash_from_string(item.get("text", ""))
        )

        item["notebook"] = notebook
        item["uuid"] = uuid
        item["file_hash"] = file_hash
        date = item.pop("date", None)
        item["created"] = timestamp(make_datetime(date))

        title = item.pop("title", None)
        if not title:
            title = make_datetime(date).strftime("%a, %b %d, %Y %I:%M %p")
        item["title"] = title

        Note(item).save()

        success += 1

    return {"skipped": skipped, "success": success}


def import_json(data):
    skipped = 0
    success = 0

    entries = data.get("entries", [])

    for entry in entries:
        if not entry.get("text", None):
            skipped += 1
            continue

        created_datetime = make_datetime(entry.pop("creationDate"), fmt="isoformat")
        edited_datetime = make_datetime(entry.pop("modifiedDate"), fmt="isoformat")
        entry["created"] = timestamp(created_datetime)
        entry["edited"] = timestamp(edited_datetime)
        entry["notebook"] = entry.get("notebook", 1)

        title = entry.get("title", None)
        if not title:
            title = created_datetime.strftime("%a, %b %d, %Y %I:%M %p")
        entry["title"] = title

        Note(entry).save()

        success += 1

    return {"skipped": skipped, "success": success}


def import_zipfile(data):
    return {}


def import_file(data):
    return {}


IMPORTERS = {
    "text/csv": import_csv,
    "application/json": import_json,
    "text/plain": import_file,
    "application/zip": import_zipfile,
}
