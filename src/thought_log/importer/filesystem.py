import frontmatter

from pathlib import Path
from typing import Dict, Union

from thought_log.utils import read_file, zettelkasten_id
from thought_log.utils.common import make_datetime
from thought_log.utils.io import write_json


def prepare_data(data: Union[frontmatter.Post, Dict, str]) -> Dict:
    """Prepare data for import"""
    import_data = {}

    if isinstance(data, frontmatter.Post):
        text = data.content
        date = data.metadata["date"]
        metadata = data.metadata
    elif isinstance(data, Dict):
        text = data.pop("text")
        date = data.pop("date")
        metadata = data
    else:
        pass

    import_data["id"] = zettelkasten_id(date)
    import_data["metadata"] = metadata
    import_data["text"] = text

    return import_data


def import_from_file(filename: Union[str, Path]):
    """Import from plaintext or markdown"""
    read_file(filename)


def import_from_directory():
    pass
