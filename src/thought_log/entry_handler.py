from typing import Dict

import frontmatter

from thought_log.classifier import Classifier
from thought_log.config import STORAGE_DIR
from thought_log.utils import zettelkasten_id


def load_entry(zkid: str):
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")

    with open(entry_filepath) as f:
        entry = frontmatter.load(f)
        return entry, entry_filepath


def write_entry(text: str):
    zkid = zettelkasten_id()
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")

    with open(entry_filepath, "a+") as f:
        post = frontmatter.load(f)
        post.content = text
        post.metadata["id"] = zettelkasten_id()
        f.write(frontmatter.dumps(post))


def classify_entry(text):
    classifier = Classifier()
    labels = classifier.classify(text, k=3, include_score=False)
    return labels
