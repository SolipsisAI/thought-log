from datetime import datetime
from typing import Dict, Union

import frontmatter
from tqdm.auto import tqdm

from thought_log.config import STORAGE_DIR
from thought_log.utils import (
    read_csv,
    zettelkasten_id,
    snakecase,
    to_datetime,
    list_entries,
)


def load_entries():
    return list(
        map(lambda e: load_entry(e).content + "\n-------\n", list_entries(STORAGE_DIR))
    )


def load_entry(zkid: Union[str, int]):
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")

    with open(entry_filepath) as f:
        entry = frontmatter.load(f)
        return entry


def write_entry(text: str, datetime_obj=None, metadata: Dict = None):
    if not datetime_obj:
        datetime_obj = datetime.now()

    if not metadata:
        metadata = {}

    zkid = zettelkasten_id(datetime_obj=datetime_obj)
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")

    with open(entry_filepath, "a+") as f:
        post = frontmatter.load(f)
        post.content = text

        # Set metadata
        metadata["id"] = int(zkid)
        metadata["timestamp"] = datetime_obj.isoformat()

        # Update metadata
        post.metadata.update(metadata)

        # Write to file
        f.write(frontmatter.dumps(post))


def import_dayone_csv(filename: str):
    """Import DayOne exported CSV"""
    rows = read_csv(filename)

    for row in tqdm(rows):
        datetime_string = row.pop("date")
        text = row.pop("text")
        metadata = dict([(snakecase(k), v) for k, v in row.items()])

        write_entry(
            text,
            datetime_obj=to_datetime(datetime_string[:-1], fmt="isoformat"),
            metadata=metadata,
        )
