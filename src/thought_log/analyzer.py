from typing import Dict, List
from thought_log.entry_handler import load_entries
from tqdm.auto import tqdm

from thought_log.config import (
    CLASSIFIER_NAMES,
    STORAGE_DIR,
)
from thought_log.utils import (
    list_entries,
    write_json,
)


DEFAULT_CLASSIFIERS = ["emotion", "sentiment", "context"]


def get_classifiers(classifier_names: List[str] = None) -> Dict:
    from thought_log.nlp.classifier import Classifier

    if not classifier_names:
        classifier_names = DEFAULT_CLASSIFIERS

    classifiers = {}

    for name in classifier_names:
        classifier_path = CLASSIFIER_NAMES[name]
        classifiers[name] = Classifier(model=classifier_path, tokenizer=classifier_path)

    return classifiers


def analyze_entries(
    reverse: bool = True,
    num_entries: int = -1,
    classifier_names: List[str] = None,
):
    if not classifier_names:
        classifier_names = DEFAULT_CLASSIFIERS

    classifiers = get_classifiers(classifier_names)

    zkids = list_entries(STORAGE_DIR, reverse=reverse, num_entries=num_entries)

    skipped = 0

    for zkid in tqdm(zkids):
        entries = load_entries(zkid)

        for entry, filepath in entries:
            entry["analysis"] = analyze_entry(
                entry, classifier_names=classifier_names, classifiers=classifiers
            )

            write_json(entry, filepath)

    print(f"Skipped {skipped}")


def analyze_entry(
    entry: Dict,
    classifier_names: List[str] = None,
    classifiers: Dict = None,
) -> Dict:
    if not classifier_names:
        classifier_names = DEFAULT_CLASSIFIERS

    if not classifiers:
        classifiers = get_classifiers(classifier_names)

    analysis = entry.get("analysis", {})

    for name in classifier_names:
        if name not in analysis:
            analysis[name] = classifiers[name].classify(entry["text"])

    return analysis


def analyze_text(text: str):
    analysis = {}
    classifiers = get_classifiers()

    for name, classifier in classifiers.items():
        analysis[name] = classifier(text)

    return analysis
