from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Dict, Union

import frontmatter
from tqdm.auto import tqdm

from thought_log.config import STORAGE_DIR, DEBUG
from thought_log.utils import get_filetype, read_csv, read_file, zettelkasten_id
from thought_log.utils.common import find_datetime, make_datetime, sanitize_text
from thought_log.utils.io import (
    generate_uuid,
    read_json,
    write_json,
    generate_hash_from_file,
    generate_hash_from_string,
)


SUPPORTED_FILETYPES = ["text/plain", "text/markdown", "text/csv", "text/json"]


def import_from_file(fp: Union[str, Path, TextIOWrapper]):
    """Import from plaintext or markdown"""
    filetype = get_filetype(fp)

    if filetype not in SUPPORTED_FILETYPES:
        return

    _hash = generate_hash_from_file(fp)

    if already_imported(_hash, None):
        if DEBUG:
            print(f"{fp} already imported. filehash: {_hash}")
        return

    data = read_file(fp)
    data = prepare_data(data, _hash)

    # store the import source
    data["metadata"].update(
        {
            "tl_source_dir": str(Path(fp).parent.absolute()),
            "tl_source_file": Path(fp).name,
        }
    )

    return import_data(data, fp)


def import_data(data, filename: str = None):
    date = data.pop("date", None)

    # If no date is found, try getting it from the name
    if not date:
        date = make_datetime(str(filename)) if filename else datetime.now()

    data["date"] = date
    zkid = zettelkasten_id(date)
    data["id"] = zkid
    _hash = data["_hash"]
    uuid = data["uuid"]

    return write_json(data, STORAGE_DIR.joinpath(f"{zkid}.{uuid}.{_hash}.json"))


def import_from_directory(dirpath: Union[str, Path]):
    """Import plain text/markdown from a directory"""
    dirpath = Path(dirpath) if isinstance(dir, str) else dirpath
    filenames = list(filter(lambda p: not p.is_dir(), dirpath.glob("**/*")))
    skipped = 0

    for filename in tqdm(filenames):
        result = import_from_file(filename)
        if not result:
            if DEBUG:
                print(f"Skipped: {filename}")
            skipped += 1

    print(f"Skipped {skipped} files")


def import_from_json(filename: str):
    """Import from a DayOne JSON export"""
    source_data = read_json(filename)
    metadata = {
        "tl_source_dir": str(Path(filename).parent.absolute()),
        "tl_source_file": Path(filename).name,
    }
    entries = source_data["entries"]
    batch_import(entries, metadata)


def import_from_csv(filename: str):
    """Import from a DayOne CSV export"""
    metadata = {
        "tl_source_dir": str(Path(filename).parent.absolute()),
        "tl_source_file": Path(filename).name,
    }
    entries = read_csv(filename)
    batch_import(entries, metadata)


def batch_import(entries, metadata):
    skipped = 0

    for entry in tqdm(entries):
        if not bool(entry.get("text")):
            skipped += 1
            continue

        entry["text"] = sanitize_text(entry["text"])
        _hash = generate_hash_from_string(entry["text"])

        if already_imported(_hash, entry.get("uuid")):
            skipped += 1
            continue

        data = prepare_data(entry, _hash)

        # store the import source
        data["metadata"].update(metadata)
        result = import_data(data)

        if not result:
            skipped += 1

    print(f"Skipped {skipped} entries")


def already_imported(_hash, _uuid) -> bool:
    found_hashes = _hash and list(STORAGE_DIR.glob(f"*.*.{_hash}.json"))
    found_uuids = _uuid and list(STORAGE_DIR.glob(f"*.{_uuid}.*.json"))
    return found_hashes or found_uuids


def prepare_data(
    data: Union[frontmatter.Post, Dict, str], _hash: str, metadata: Dict = None
) -> Dict:
    """Prepare data for import"""
    prepared_data = {"_hash": _hash}

    if not metadata:
        metadata = {}

    date = None
    uuid = None

    if isinstance(data, frontmatter.Post):
        text = data.content
        date = data.metadata.get("date") or find_datetime(text)
        metadata.update(data.metadata)
        uuid = metadata.get("uuid")
    elif isinstance(data, Dict):
        text = data.pop("text", "")
        date = data.pop("date", None) or data.pop("creationDate", None)
        metadata.update(data)
        uuid = data.get("uuid")
    else:
        text = data
        date = find_datetime(text)

    prepared_data["date"] = make_datetime(date) if date else None
    prepared_data["id"] = zettelkasten_id(date) if date else None
    prepared_data["uuid"] = uuid if uuid else generate_uuid()
    prepared_data["metadata"] = metadata
    prepared_data["text"] = text

    return prepared_data
