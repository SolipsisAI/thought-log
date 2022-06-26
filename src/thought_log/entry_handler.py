from datetime import datetime

import frontmatter

from thought_log.config import STORAGE_DIR
from thought_log.utils import zettelkasten_id


def load_entry(zkid: str):
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")

    with open(entry_filepath) as f:
        entry = frontmatter.load(f)
        return entry, entry_filepath


def write_entry(text: str, datetime_obj=None):
    if not datetime_obj:
        datetime_obj = datetime.now()

    zkid = zettelkasten_id(datetime_obj=datetime_obj)
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")

    with open(entry_filepath, "a+") as f:
        post = frontmatter.load(f)
        post.content = text
        post.metadata["id"] = zettelkasten_id()
        post.metadata["timestamp"] = datetime_obj.strftime("%Y-%m-%d_%H:%M:%S")
        f.write(frontmatter.dumps(post))
