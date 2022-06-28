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
    display_text,
    hline,
)


def show_entries(reverse: bool, num_entries: int, show_id: bool):
    if not STORAGE_DIR:
        raise ValueError(
            "Please configure a storage_dir with: "
            "thought-log configure -d path/to/storage_dir"
        )

    entry_ids = list_entries(STORAGE_DIR, reverse=reverse, num_entries=num_entries)

    for zkid in entry_ids:
        entry = load_entry(zkid)

        # Make timestamp prettier
        timestamp = entry.metadata["timestamp"]
        datetime_obj = to_datetime(timestamp, fmt="isoformat")
        datetime_str = datetime_obj.strftime("%x %X")

        # Format display
        display = f"[{datetime_str}]\n\n{display_text(entry.content)}\n\n{hline()}\n\n"
        display = f"ID: {zkid}\n{display}" if show_id else display
        yield display


def load_entry(zkid: Union[str, int]):
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")

    with open(entry_filepath) as f:
        entry = frontmatter.load(f)
        return entry


def add_entry(filename: str):
    with open(filename, "r") as f:
        entry = frontmatter.load(f)
        write_entry(entry.content, metadata={"imported_from": "file", **entry.metadata})


def write_entry(text: str, datetime_obj=None, metadata: Dict = None):
    if not datetime_obj:
        datetime_obj = datetime.now()

    if not metadata:
        metadata = {}

    zkid = zettelkasten_id(datetime_obj=datetime_obj)
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")

    if entry_filepath.exists():
        return

    return update_entry(zkid, text, metadata)


def update_entry(
    zkid: Union[str, int],
    text: str,
    metadata: Dict = None,
    create_if_missing: bool = True,
):
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")

    if not entry_filepath.exists() and not create_if_missing:
        raise ValueError(f"{entry_filepath} does not exist")

    if not metadata:
        metadata = {}

    with open(entry_filepath, "a+") as f:
        post = frontmatter.load(f)

        # Update entry content if text is different
        if post.content != text:
            post.content = text

        # Update metadata
        post.metadata.update(metadata)

        # Write to file
        f.write(frontmatter.dumps(post))

        return post


def import_from_csv(filename: str):
    """Import DayOne exported CSV"""
    rows = read_csv(filename)
    skipped = 0

    for row in tqdm(rows):
        datetime_string = row.pop("date")
        text = row.pop("text")
        metadata = dict([(snakecase(k), v) for k, v in row.items()])
        metadata["imported_from"] = "dayone"

        entry = write_entry(
            text,
            datetime_obj=to_datetime(datetime_string[:-1], fmt="isoformat"),
            metadata=metadata,
        )

        if not entry:
            skipped += 1

    print(f"Skipped: {skipped}")
