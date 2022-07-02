from datetime import datetime

from pathlib import Path
from typing import Dict, Union

import frontmatter

from thought_log.config import STORAGE_DIR
from thought_log.utils import get_filetype, read_csv, read_file, zettelkasten_id
from thought_log.utils.common import find_datetime, make_datetime
from thought_log.utils.io import write_json


SUPPORTED_FILETYPES = ["text/plain", "text/markdown", "text/csv"]


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


def import_from_file(filename: Union[str, Path]):
    """Import from plaintext or markdown"""
    filetype = get_filetype(filename)

    if filetype not in SUPPORTED_FILETYPES:
        print(f"{filetype} not supported")
        return

    data = prepare_data(read_file(filename))

    # If no date is found, try getting it from the name
    if not data.get("date"):
        date = make_datetime(str(filename)) or datetime.now()
        data["date"] = date
        data["id"] = zettelkasten_id(date)

    zkid = data["id"]
    write_json(data, STORAGE_DIR.joinpath(f"{zkid}.json"))


def import_from_directory():
    """Import from a directory"""
