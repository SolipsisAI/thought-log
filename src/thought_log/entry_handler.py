from typing import Union

from thought_log.config import STORAGE_DIR
from thought_log.utils import (
    display_text,
    hline,
    list_entries,
    read_json,
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
            analysis = entry.get("analysis", {})

            # Get emotion
            emotion = analysis.get("emotion")
            display_emotion = f"mood: {emotion}\n" if emotion else ""

            # Get sentiment
            sentiment = analysis.get("sentiment")
            display_sentiment = f"sentiment: {sentiment}\n" if sentiment else ""

            # Get context
            context = analysis.get("context")
            display_context = f"context: {context}\n" if context else ""

            # Get text
            text = entry["text"]

            # Format display
            display = f"[{datetime_str}]\n\n{display_emotion}{display_sentiment}{display_context}\n\n{display_text(text)}\n\n{hline()}\n\n"
            uuid = entry["uuid"]
            _hash = entry["_hash"]
            display = f"ID: {zkid}.{uuid}.{_hash}\n{display}" if show_id else display
            yield display


def load_entries(zkid: Union[str, int]):
    entry_filepaths = STORAGE_DIR.glob(f"{zkid}.*.*.json")
    return list(map(load_entry, entry_filepaths))


def load_entry(filepath):
    return read_json(filepath), filepath
