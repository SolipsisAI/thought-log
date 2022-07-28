from typing import List, Union

from thought_log.config import DEBUG, STORAGE_DIR
from thought_log.utils import (
    display_text,
    hline,
    list_entries,
    read_json,
)

SUPPORTED_EXTS = ["markdown", "md", "txt"]

ENTRY_ATTRS = ["uuid", "date", "text", "analysis"]

ENTRY_TEMPLATE = """
[{date}] {uuid}
{analysis}
{text}
{hline}
"""

ANALYSIS_TEMPLATE = """
MOOD: {emotion}
SENTIMENT: {sentiment}
CONTEXT: {context}
"""


def load_entries(zkid: Union[str, int]):
    entry_filepaths = STORAGE_DIR.glob(f"{zkid}.*.*.json")
    return list(map(load_entry, entry_filepaths))


def load_entry(filepath):
    return read_json(filepath), filepath


def show_entries(reverse: bool, num_entries: int, show_id: bool):
    if not STORAGE_DIR:
        raise ValueError(
            "Please configure a storage_dir with: "
            "thought-log configure -d path/to/storage_dir"
        )

    zkids = list_entries(STORAGE_DIR, reverse=reverse, num_entries=num_entries)

    additional_attrs = []
    if show_id:
        additional_attrs.append("uuid")

    for zkid in zkids:
        entries = load_entries(zkid)

        for entry, _ in entries:
            yield show_entry(entry, additional_attrs)


def show_entry(entry, additional_attrs: List[str]):
    attrs = list(set(ENTRY_ATTRS).union(additional_attrs))

    values = {attr: entry.get(attr) for attr in attrs}
    values["text"] = display_text(entry["text"])
    values["analysis"] = format_analysis(values["analysis"])
    values["hline"] = hline()

    return ENTRY_TEMPLATE.format(**values)


def format_analysis(analysis):
    return ANALYSIS_TEMPLATE.format(**analysis)
