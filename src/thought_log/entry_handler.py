from typing import Dict

import frontmatter

from thought_log.classifier import Classifier
from thought_log.config import STORAGE_DIR
from thought_log.utils import zettelkasten_id


def read_entry(zkid: str):
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")
    with open(entry_filepath) as f:
        entry = frontmatter.load(f)
        return entry, entry_filepath


def write_entry(text: str, metadata: Dict = None):
    zkid = zettelkasten_id()

    entry, entry_filepath = read_entry(zkid)
    entry.metadata.update(metadata)
    entry.content = text

    with open(entry_filepath, "w+") as f:
        frontmatter.dump(entry, f)


def classify_entry(text):
    classifier = Classifier()
    labels = classifier.classify(text, k=3, include_score=False)
    return labels
