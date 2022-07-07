from thought_log.entry_handler import load_entries
from tqdm.auto import tqdm

from thought_log.config import (
    EMOTION_CLASSIFIER_NAME,
    SENTIMENT_CLASSIFIER_NAME,
    STORAGE_DIR,
)
from thought_log.nlp.utils import split_paragraphs, tokenize
from thought_log.utils import (
    list_entries,
    write_json,
)


def classify_entries(
    reverse: bool = True,
    num_entries: int = -1,
    force: bool = False,
):
    from thought_log.nlp.classifier import Classifier

    emotion_classifier = Classifier(
        model=EMOTION_CLASSIFIER_NAME, tokenizer=EMOTION_CLASSIFIER_NAME
    )
    sentiment_classifier = Classifier(
        model=SENTIMENT_CLASSIFIER_NAME,
        tokenizer=SENTIMENT_CLASSIFIER_NAME,
    )

    zkids = list_entries(STORAGE_DIR, reverse=reverse, num_entries=num_entries)

    skipped = 0

    for zkid in tqdm(zkids):
        entries = load_entries(zkid)

        for entry, filepath in entries:
            analysis = entry.get("analysis", {})
            needs_emotion = "emotion" not in analysis
            needs_sentiment = "sentiment" not in analysis

            if not needs_emotion and not needs_sentiment and not force:
                continue

            entry["analysis"] = {}

            if needs_emotion or force:
                emotion = emotion_classifier.classify(entry["text"])
                entry["analysis"] = emotion

            if needs_sentiment or force:
                sentiment = sentiment_classifier.classify(entry["text"])
                entry["analysis"] = sentiment

            write_json(entry, filepath)

    print(f"Skipped {skipped}")
