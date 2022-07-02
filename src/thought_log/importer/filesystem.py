import frontmatter

from pathlib import Path
from typing import Dict, Union

from thought_log.config import STORAGE_DIR
from thought_log.utils import get_filetype, read_csv, read_file, zettelkasten_id
from thought_log.utils.common import make_datetime
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
        date = data.pop("date")
        metadata = data
    else:
        text = data
        date = make_datetime(text)

    import_data["id"] = zettelkasten_id(date)
    import_data["date"] = make_datetime(date)
    import_data["metadata"] = metadata
    import_data["text"] = text

    return import_data


def import_from_file(filename: Union[str, Path]):
    """Import from plaintext or markdown"""
    filetype = get_filetype(filename)

    if filetype not in SUPPORTED_FILETYPES:
        print(f"{filetype} not supported")
        return

    # TODO: get datetime from the filename
    data = prepare_data(read_file(filename))
    zkid = data["id"]
    write_json(data, STORAGE_DIR.joinpath(f"{zkid}.json"))


def import_from_directory():
    """Import from a directory"""
