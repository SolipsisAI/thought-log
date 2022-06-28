from datetime import datetime
from typing import Dict, Union

import frontmatter
from tqdm.auto import tqdm

from thought_log.config import STORAGE_DIR, EMOTION_CLASSIFIER_NAME
from thought_log.utils import (
    display_text,
    frequency,
    get_top_labels,
    hline,
    list_entries,
    read_csv,
    snakecase,
    to_datetime,
    write_json,
    zettelkasten_id,
)
from thought_log.nlp.utils import split_paragraphs, tokenize


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

        # Get emotion
        emotion = entry.metadata.get("emotion", "")

        # Format display
        display = f"[{datetime_str}] mood: {emotion}\n\n{display_text(entry.content)}\n\n{hline()}\n\n"
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

    metadata["id"] = int(zkid)
    metadata["timestamp"] = datetime_obj.isoformat()

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

    if not entry_filepath.exists():
        entry_filepath.touch()

    if not metadata:
        metadata = {}

    post = frontmatter.load(entry_filepath)
    post.content = text
    post.metadata.update(metadata)

    with open(entry_filepath, "w+") as f:
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


def classify_entries(
    classifier_name: str = EMOTION_CLASSIFIER_NAME,
    reverse: bool = True,
    num_entries: int = -1,
):
    from thought_log.nlp.classifier import Classifier

    classifier = Classifier(model=classifier_name, tokenizer=classifier_name)
    entry_ids = list_entries(STORAGE_DIR, reverse=reverse, num_entries=num_entries)

    for entry_id in tqdm(entry_ids):
        entry = load_entry(entry_id)
        paragraph_labels = classify_entry(classifier, entry)
        label_frequency = frequency(paragraph_labels)

        # Save labels for each paragraph and their scores
        labels_filepath = STORAGE_DIR.joinpath(f"{entry_id}.json")
        data = {
            "paragraphs": paragraph_labels,
            "frequency": label_frequency,
        }
        write_json(data, labels_filepath)

        # Update entry with emotion tag
        text = entry.content
        metadata = {"emotion": get_top_labels(label_frequency, k=1)}
        update_entry(entry_id, text, metadata)


def classify_entry(
    classifier, entry: Union[str, frontmatter.Post], split: bool = True, k: int = 1
):
    """Assign emotion classifiers to an entry/text"""
    if isinstance(entry, frontmatter.Post):
        text = entry.content
    else:
        text = entry

    doc = tokenize(text)
    classify = lambda t: dict(
        labels=classifier.classify(t, k=k, include_score=True),
        text=t.strip(),
    )

    if not split:
        results = [classify(doc.text)]
    else:
        paragraphs = list(map(lambda p: p.text, split_paragraphs(doc)))
        results = list(map(classify, paragraphs))

    return results
