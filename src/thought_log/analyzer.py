from thought_log.entry_handler import load_entries
from tqdm.auto import tqdm

from thought_log.config import (
    EMOTION_CLASSIFIER_NAME,
    SENTIMENT_CLASSIFIER_NAME,
    CLASSIFIER_NAME,
    STORAGE_DIR,
)
from thought_log.utils import (
    list_entries,
    write_json,
)


def get_classifiers():
    from thought_log.nlp.classifier import Classifier

    emotion_classifier = Classifier(
        model=EMOTION_CLASSIFIER_NAME, tokenizer=EMOTION_CLASSIFIER_NAME
    )
    sentiment_classifier = Classifier(
        model=SENTIMENT_CLASSIFIER_NAME,
        tokenizer=SENTIMENT_CLASSIFIER_NAME,
    )
    context_classifier = Classifier(
        model=CLASSIFIER_NAME,
        tokenizer=CLASSIFIER_NAME,
    )

    return {
        "emotion": emotion_classifier,
        "sentiment": sentiment_classifier,
        "context": context_classifier,
    }


def analyze_entries(
    reverse: bool = True,
    num_entries: int = -1,
    update: str = None,
):
    classifiers = get_classifiers()

    zkids = list_entries(STORAGE_DIR, reverse=reverse, num_entries=num_entries)

    skipped = 0

    for zkid in tqdm(zkids):
        entries = load_entries(zkid)

        for entry, filepath in entries:
            entry["analysis"] = analyze_entry(entry, classifiers, update)

            write_json(entry, filepath)

    print(f"Skipped {skipped}")


def analyze_entry(entry, classifiers, update):
    analysis = entry.get("analysis", {})

    needs_emotion = "emotion" not in analysis or update == "emotion"
    needs_sentiment = "sentiment" not in analysis or update == "sentiment"
    needs_context = "context" not in analysis or update == "context"

    if not needs_emotion and not needs_sentiment and not needs_context:
        return analysis

    if needs_emotion:
        analysis["emotion"] = classifiers["emotion"].classify(entry["text"])

    if needs_sentiment:
        analysis["sentiment"] = classifiers["sentiment"].classify(entry["text"])

    if needs_context:
        analysis["context"] = classifiers["context"].classify(entry["text"], k=2)

    return analysis
