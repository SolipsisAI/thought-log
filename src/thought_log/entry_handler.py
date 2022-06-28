from copy import copy
from datetime import datetime
import json
from json.decoder import JSONDecodeError
from typing import Dict, Union
from click.types import Path

import frontmatter
from tqdm.auto import tqdm

from thought_log.config import CLASSIFIER_NAME, EMOTION_CLASSIFIER_NAME, STORAGE_DIR
from thought_log.nlp.utils import split_paragraphs, tokenize
from thought_log.utils import (
    display_text,
    find_datetime,
    frequency,
    get_top_labels,
    hline,
    list_entries,
    read_csv,
    read_json,
    snakecase,
    to_datetime,
    write_json,
    zettelkasten_id,
)

SUPPORTED_EXTS = ["markdown", "md", "txt"]


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
        mood = f"mood: {emotion}\n" if emotion else ""

        # Get context
        context = entry.metadata.get("context", "")
        tags = f"tags: {context}\n" if context else ""

        # Format display
        display = f"[{datetime_str}]\n\n{mood}{tags}\n\n{display_text(entry.content)}\n\n{hline()}\n\n"
        display = f"ID: {zkid}\n{display}" if show_id else display
        yield display


def load_entry(zkid: Union[str, int], mode: str = "r"):
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")

    with open(entry_filepath, mode) as f:
        entry = frontmatter.load(f)
        return entry


def write_entry(text: str, datetime_obj=None, metadata: Dict = None):
    if not metadata:
        metadata = {}

    if not datetime_obj:
        timestamp = metadata.get("timestamp") or metadata.get("date")
        datetime_obj = datetime.now() if not timestamp else to_datetime(timestamp)

    zkid = zettelkasten_id(datetime_obj=datetime_obj)
    entry_filepath = STORAGE_DIR.joinpath(f"{zkid}.txt")

    if entry_filepath.exists():
        return frontmatter.load(entry_filepath)

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


def import_from_file(filename: Union[str, Path]):
    """Import from a text file (txt, markdown)"""
    filepath = Path(filename) if isinstance(filename, str) else filename

    if filepath.suffix[1:] not in SUPPORTED_EXTS:
        print(f"{filepath} is not supported")
        return

    source_entry = None
    with open(filepath, "r") as f:
        source_entry = frontmatter.load(f)

    history_filepath = STORAGE_DIR.joinpath(".import_history")
    history_filepath.touch()

    try:
        history = read_json(history_filepath)
    except JSONDecodeError:
        history = {}

    already_imported = filepath.name in history

    if already_imported:
        print(f"Already imported {filepath.name}")
        return

    text = source_entry.content
    datetime_obj = find_datetime(str(filepath))
    entry = write_entry(text, datetime_obj=datetime_obj)
    zkid = entry.metadata["id"]
    history.update({filepath.name: zkid})
    write_json(history, history_filepath)

    return entry


def import_from_csv(filename: str):
    """Import DayOne exported CSV"""
    rows = read_csv(filename)
    skipped = 0

    for row in tqdm(rows):
        datetime_string = row.pop("date")
        text = row.pop("text")
        metadata = dict([(snakecase(k), v) for k, v in row.items()])
        metadata["imported_from"] = str(filename)

        entry = write_entry(
            text,
            datetime_obj=to_datetime(datetime_string[:-1], fmt="isoformat"),
            metadata=metadata,
        )

        if not entry:
            skipped += 1

    print(f"Skipped: {skipped}")


def import_from_directory(directory_name: Union[str, Path]):
    dirpath = (
        Path(directory_name) if isinstance(directory_name, str) else directory_name
    )

    if not dirpath.is_dir():
        print(f"{dirpath} is not a directory")
        return

    if not dirpath.exists():
        print(f"{dirpath} does not exist")
        return

    filepaths = list(
        filter(lambda p: p.suffix[1:] in SUPPORTED_EXTS, dirpath.glob("**/*"))
    )

    skipped = 0

    for filepath in tqdm(filepaths):
        entry = import_from_file(filepath)
        if not entry:
            skipped += 1

    print(f"Skipped {skipped}")


def classify_entries(
    reverse: bool = True,
    num_entries: int = -1,
):
    from thought_log.nlp.classifier import Classifier

    classifiers = {
        "emotion": Classifier(
            model=EMOTION_CLASSIFIER_NAME, tokenizer=EMOTION_CLASSIFIER_NAME
        ),
        "context": Classifier(model=CLASSIFIER_NAME, tokenizer=CLASSIFIER_NAME),
    }

    entry_ids = list_entries(STORAGE_DIR, reverse=reverse, num_entries=num_entries)

    skipped = 0

    for entry_id in tqdm(entry_ids):
        entry = load_entry(entry_id)

        needs_emotion = not bool(entry.metadata.get("emotion"))
        needs_context = not bool(entry.metadata.get("context"))
        needs_analysis = needs_emotion or needs_context

        if not needs_analysis:
            skipped += 1
            continue

        paragraph_labels = classify_entry(classifiers, entry)

        emotion_frequency = frequency(paragraph_labels, key="emotion")
        context_frequency = frequency(paragraph_labels, key="context")

        # Save labels for each paragraph and their scores
        labels_filepath = STORAGE_DIR.joinpath(f"{entry_id}.json")
        data = {
            "paragraphs": paragraph_labels,
            "frequency": {
                "emotion": emotion_frequency,
                "context": context_frequency,
            },
        }
        write_json(data, labels_filepath)

        # Update entry with emotion tag
        text = entry.content
        metadata = {
            "emotion": get_top_labels(emotion_frequency, k=1),
            "context": get_top_labels(context_frequency, k=3),
        }
        update_entry(entry_id, text, metadata)

    print(f"Skipped {skipped}")


def classify_entry(
    classifiers,
    entry: Union[str, frontmatter.Post],
    split: bool = True,
    emotion_k: int = 1,
    context_k: int = 3,
):
    """Assign emotion classifiers to an entry/text"""
    if isinstance(entry, frontmatter.Post):
        text = entry.content
    else:
        text = entry

    doc = tokenize(text)

    classify = lambda t: dict(
        emotion=classifiers["emotion"].classify(t, k=emotion_k, include_score=True),
        context=classifiers["context"].classify(t, k=context_k, include_score=True),
        text=t.strip(),
    )

    if not split:
        results = [classify(doc.text)]
    else:
        paragraphs = list(map(lambda p: p.text, split_paragraphs(doc)))
        results = list(map(classify, paragraphs))

    return results
