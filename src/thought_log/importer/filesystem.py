from datetime import datetime
from pathlib import Path
from typing import Dict, Union

import frontmatter
from tqdm.auto import tqdm

from thought_log.config import STORAGE_DIR
from thought_log.utils import get_filetype, read_csv, read_file, zettelkasten_id
from thought_log.utils.common import find_datetime, make_datetime
from thought_log.utils.io import write_json


SUPPORTED_FILETYPES = ["text/plain", "text/markdown", "text/csv"]


def import_from_file(filename: Union[str, Path]):
    """Import from plaintext or markdown"""
    filetype = get_filetype(filename)

    if filetype not in SUPPORTED_FILETYPES:
        return

    post = read_file(filename)
    data = prepare_data(post)

    return import_data(data, filename)


def prepare_data(data: Union[frontmatter.Post, Dict, str]) -> Dict:
    """Prepare data for import"""
    prepared_data = {}
    metadata = {}
    date = None

    if isinstance(data, frontmatter.Post):
        text = data.content
        date = data.metadata.get("date")
        metadata = data.metadata
    elif isinstance(data, Dict):
        text = data.pop("text")
        date = data.pop("date", None)
        metadata = data
    else:
        text = data
        date = find_datetime(text)

    prepared_data["date"] = make_datetime(date) if date else None
    prepared_data["id"] = zettelkasten_id(date) if date else None
    prepared_data["metadata"] = metadata
    prepared_data["text"] = text

    return prepared_data


def import_data(data, filename: str = None):
    # If no date is found, try getting it from the name
    if not data.get("date") and filename:
        date = make_datetime(str(filename)) or datetime.now()
        data["date"] = date
        data["id"] = zettelkasten_id(date)

    zkid = data["id"]

    if already_imported(zkid):
        return

    return write_json(data, STORAGE_DIR.joinpath(f"{zkid}.json"))


def import_from_directory(dirpath: Union[str, Path]):
    """Import from a directory"""
    dirpath = Path(dirpath) if isinstance(dir, str) else dirpath
    filenames = list(dirpath.glob("**/*"))
    skipped = 0

    for filename in tqdm(filenames):
        result = import_from_file(filename)
        if not result:
            print(f"Skipped: {filename}")
            skipped += 1

    print(f"Skipped {skipped} files")


def import_from_csv(filename: str):
    rows = read_csv(filename)
    skipped = 0

    for row in tqdm(rows):
        data = prepare_data(row)
        result = import_data(data)
        if not result:
            skipped += 1

    print(f"Skipped {skipped} rows")


def already_imported(zkid):
    return STORAGE_DIR.joinpath(f"{zkid}.json").exists()
