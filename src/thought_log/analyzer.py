from thought_log.entry_handler import load_entries
from tqdm.auto import tqdm

from thought_log.config import (
    CLASSIFIER_NAME,
    EMOTION_CLASSIFIER_NAME,
    SENTIMENT_CLASSIFIER_NAME,
    STORAGE_DIR,
)
from thought_log.nlp.utils import split_paragraphs, tokenize
from thought_log.utils import (
    frequency,
    get_top_labels,
    list_entries,
    write_json,
)


def classify_entries(
    reverse: bool = True,
    num_entries: int = -1,
    force: bool = False,
):
    from thought_log.nlp.classifier import Classifier

    classifier = Classifier(
        model=EMOTION_CLASSIFIER_NAME, tokenizer=EMOTION_CLASSIFIER_NAME
    )

    zkids = list_entries(STORAGE_DIR, reverse=reverse, num_entries=num_entries)

    skipped = 0

    for zkid in tqdm(zkids):
        entries = load_entries(zkid)

        for entry, filepath in entries:
            needs_emotion = "emotion" not in entry.get("analysis", {})

            if not needs_emotion and not force:
                continue

            emotion = classifier.classify(entry["text"])
            entry["analysis"] = {"emotion": emotion}
            write_json(entry, filepath)

    print(f"Skipped {skipped}")


def classify_entry(
    classifiers,
    text: str,
    split: bool = True,
    emotion_k: int = 1,
    context_k: int = 3,
    sentiment_k: int = 1,
):
    """Assign emotion classifiers to an entry/text"""
    doc = tokenize(text)

    classify = lambda t: dict(
        emotion=classifiers["emotion"].classify(t, k=emotion_k, include_score=True),
        context=classifiers["context"].classify(t, k=context_k, include_score=True),
        text=t.strip(),
        sentiment=classifiers["sentiment"].classify(
            t, k=sentiment_k, include_score=True
        ),
    )

    if not split:
        results = [classify(doc.text)]
    else:
        paragraphs = list(map(lambda p: p.text, split_paragraphs(doc)))
        results = list(map(classify, paragraphs))

    return results
