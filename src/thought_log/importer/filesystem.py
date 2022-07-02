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

    return write_data(data)


def prepare_data(data: Union[frontmatter.Post, Dict, str]) -> Dict:
    """Prepare data for import"""
    import_data = {}
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

    import_data["date"] = make_datetime(date) if date else None
    import_data["id"] = zettelkasten_id(date) if date else None
    import_data["metadata"] = metadata
    import_data["text"] = text

    return import_data


def write_data(data, filename: str = None):
    # If no date is found, try getting it from the name
    if not data.get("date") and filename:
        date = make_datetime(str(filename)) or datetime.now()
        data["date"] = date
        data["id"] = zettelkasten_id(date)

    zkid = data["id"]

    if already_imported(zkid):
        return

    return write_json(data, STORAGE_DIR.joinpath(f"{zkid}.json"))


def import_from_directory():
    """Import from a directory"""


def import_from_csv(filename: str):
    rows = read_csv(filename)
    skipped = 0

    for row in tqdm(rows):
        data = prepare_data(row)
        result = write_data(data)
        if not result:
            skipped += 1

    print(f"Skipped {skipped} rows")


def already_imported(zkid):
    return STORAGE_DIR.joinpath(f"{zkid}.json").exists()
