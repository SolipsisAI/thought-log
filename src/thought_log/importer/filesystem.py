from datetime import datetime
from pathlib import Path
from typing import Dict, Union

import frontmatter
from tqdm.auto import tqdm

from thought_log.config import STORAGE_DIR
from thought_log.utils import get_filetype, read_csv, read_file, zettelkasten_id
from thought_log.utils.common import find_datetime, make_datetime, sanitize_text
from thought_log.utils.io import (
    read_json,
    write_json,
    generate_hash_from_file,
    generate_hash_from_string,
)


SUPPORTED_FILETYPES = ["text/plain", "text/markdown", "text/csv", "text/json"]


def import_from_file(filename: Union[str, Path]):
    """Import from plaintext or markdown"""
    filetype = get_filetype(filename)

    if filetype not in SUPPORTED_FILETYPES:
        return

    _hash = generate_hash_from_file(filename)

    if already_imported(_hash):
        print(f"{filename} already imported. filehash: {_hash}")
        return

    data = read_file(filename)
    data = prepare_data(data, _hash)
    # store the import source
    data["metadata"].update(
        {
            "tl_source_dir": str(Path(filename).parent.absolute()),
            "tl_source_file": Path(filename).name,
        }
    )
    return import_data(data, filename)


def import_data(data, filename: str = None):
    # If no date is found, try getting it from the name
    if not data.get("date") and filename:
        date = make_datetime(str(filename)) or datetime.now()
        data["date"] = date
        data["id"] = zettelkasten_id(date)

    zkid = data["id"]
    _hash = data["_hash"]

    return write_json(data, STORAGE_DIR.joinpath(f"{zkid}.{_hash}.json"))


def import_from_directory(dirpath: Union[str, Path]):
    """Import from a directory"""
    dirpath = Path(dirpath) if isinstance(dir, str) else dirpath
    filenames = list(filter(lambda p: not p.is_dir(), dirpath.glob("**/*")))
    skipped = 0

    for filename in tqdm(filenames):
        result = import_from_file(filename)
        if not result:
            print(f"Skipped: {filename}")
            skipped += 1

    print(f"Skipped {skipped} files")


def import_from_json(filename: str):
    source_data = read_json(filename)
    metadata = {
        "tl_source_dir": str(Path(filename).parent.absolute()),
        "tl_source_file": Path(filename).name,
    }
    entries = source_data["entries"]
    batch_import(entries, metadata)


def import_from_csv(filename: str):
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

        if already_imported(_hash):
            skipped += 1
            continue

        data = prepare_data(entry, _hash)

        # store the import source
        data["metadata"].update(metadata)
        result = import_data(data)

        if not result:
            skipped += 1

    print(f"Skipped {skipped} entries")


def already_imported(_hash) -> bool:
    matching_files = list(STORAGE_DIR.glob(f"*.{_hash}.json"))
    return bool(matching_files)


def prepare_data(data: Union[frontmatter.Post, Dict, str], _hash: str) -> Dict:
    """Prepare data for import"""
    prepared_data = {"_hash": _hash}
    metadata = {}
    date = None

    if isinstance(data, frontmatter.Post):
        text = data.content
        date = data.metadata.get("date")
        metadata = data.metadata
    elif isinstance(data, Dict):
        text = data.pop("text", "")
        date = data.pop("date", None) or data.pop("creationDate", None)
        metadata = data
    else:
        text = data
        date = find_datetime(text)

    prepared_data["date"] = make_datetime(date) if date else None
    prepared_data["id"] = zettelkasten_id(date) if date else None
    prepared_data["metadata"] = metadata
    prepared_data["text"] = text

    return prepared_data
