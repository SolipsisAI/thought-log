from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Dict, Union

import frontmatter
from thought_log.utils.common import datestring, find_datetime
from tqdm.auto import tqdm

from thought_log.config import STORAGE_DIR, DEBUG
from thought_log.enums import SupportedFiletypes
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


READERS = {
    SupportedFiletypes.CSV.value: read_csv,
    SupportedFiletypes.JSON.value: read_json,
    SupportedFiletypes.PLAIN.value: read_file,
    SupportedFiletypes.ZIP.value: read_zipfile,
}


def import_data(fp, filetype=None):
    if not filetype:
        filetype = get_filetype(fp)

    if filetype not in SupportedFiletypes:
        return

    if filetype != "application/zip":
        fp = TextIOWrapper(fp)

    data = READERS[filetype](fp)

    return IMPORTERS[filetype](data)


def import_csv(data):
    skipped = 0
    success = 0
    total = len(data)

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

    return {"skipped": skipped, "success": success, "total": total}


def import_json(data):
    skipped = 0
    success = 0

    entries = data.get("entries", [])
    total = len(entries)

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
            title = datestring(created_datetime)
        entry["title"] = title

        Note(entry).save()

        success += 1

    return {"skipped": skipped, "success": success}


def import_zipfile(data):
    total = len(data)
    success = 0

    entries = sorted(
        list(filter(lambda e: e is not None, map(process_entry, data))),
        key=lambda e: e["created"],
    )

    for entry in entries:
        Note(entry).save()

    return {"skipped": total - success, "success": success, "total": total}


def process_entry(entry):
    if not any([bool(entry.content), bool(entry)]):
        return None

    if isinstance(entry, frontmatter.Post):
        text = entry.content
        date = entry.metadata.get("date") or find_datetime(text)
        metadata = entry.metadata
        uuid = metadata.get("uuid", generate_uuid())
        notebook = entry.metadata.get("notebook", 1)
        title = entry.metadata.get("title", datestring(date))
    else:
        text = entry
        date = find_datetime(text)
        uuid = generate_uuid()
        notebook = 1
        title = datestring(date)

    return {
        "title": title,
        "text": text,
        "created": timestamp(date),
        "uuid": uuid,
        "notebook": notebook,
    }


def import_file(data):
    return {}


IMPORTERS = {
    SupportedFiletypes.CSV.value: import_csv,
    SupportedFiletypes.JSON.value: import_json,
    SupportedFiletypes.PLAIN.value: import_file,
    SupportedFiletypes.ZIP.value: import_zipfile,
}
