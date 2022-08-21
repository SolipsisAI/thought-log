from typing import List, Union

from thought_log.importer.filesystem import import_data, prepare_data
from thought_log.config import DEBUG, STORAGE_DIR
from thought_log.utils import (
    display_text,
    hline,
    list_entries,
    read_json,
)
from thought_log.utils.io import generate_hash_from_string
from thought_log.weather import get_weather_metadata

SUPPORTED_EXTS = ["markdown", "md", "txt"]

ENTRY_ATTRS = ["date", "text", "analysis"]

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

    if "uuid" not in additional_attrs:
        values["uuid"] = ""

    values["text"] = display_text(entry["text"])
    values["analysis"] = format_analysis(values["analysis"])
    values["hline"] = hline()

    return ENTRY_TEMPLATE.format(**values)


def format_analysis(analysis):
    formatted = ""
    for k, v in analysis.items():
        formatted += f"{k.upper()}: {v}\n"
    return formatted


def write_entry(text, has_weather: bool = True):
    metadata = {"weather": get_weather_metadata()} if has_weather else None
    data = prepare_data(
        {"text": text}, _hash=generate_hash_from_string(text), metadata=metadata
    )
    return import_data(data)
