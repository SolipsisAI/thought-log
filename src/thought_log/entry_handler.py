from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Dict, Union

import frontmatter
from click.types import Path
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
    make_datetime,
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

    zkids = list_entries(STORAGE_DIR, reverse=reverse, num_entries=num_entries)

    for zkid in zkids:
        entries = load_entries(zkid)

        for entry, _ in entries:
            datetime_str = entry["date"]
            metadata = entry["metadata"]

            # Get emotion
            emotion = metadata.get("emotion", "")
            mood = f"mood: {emotion}\n" if emotion else ""

            # Get context
            context = metadata.get("context", "")
            tags = f"tags: {context}\n" if context else ""

            # Get text
            text = entry["text"]

            # Format display
            display = f"[{datetime_str}]\n\n{mood}{tags}\n\n{display_text(text)}\n\n{hline()}\n\n"
            display = f"ID: {zkid}\n{display}" if show_id else display
            yield display


def load_entries(zkid: Union[str, int]):
    entry_filepaths = STORAGE_DIR.glob(f"{zkid}.*.*.json")
    return list(map(load_entry, entry_filepaths))


def load_entry(filepath):
    return read_json(filepath), filepath


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

    zkids = list_entries(STORAGE_DIR, reverse=reverse, num_entries=num_entries)

    skipped = 0

    for zkid in tqdm(zkids):
        entries = load_entries(zkid)

        for entry in entries:
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
            analysis = {
                "paragraphs": paragraph_labels,
                "frequency": {
                    "emotion": emotion_frequency,
                    "context": context_frequency,
                },
            }
            # Update entry with emotion tag
            analysis["all_labels"] = {
                "emotion": get_top_labels(emotion_frequency, k=1),
                "context": get_top_labels(context_frequency, k=3),
            }

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
