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

    classifiers = {
        "emotion": Classifier(
            model=EMOTION_CLASSIFIER_NAME, tokenizer=EMOTION_CLASSIFIER_NAME
        ),
        "sentiment": Classifier(
            model=SENTIMENT_CLASSIFIER_NAME, tokenizer=SENTIMENT_CLASSIFIER_NAME
        ),
        "context": Classifier(model=CLASSIFIER_NAME, tokenizer=CLASSIFIER_NAME),
    }

    zkids = list_entries(STORAGE_DIR, reverse=reverse, num_entries=num_entries)

    skipped = 0

    for zkid in tqdm(zkids):
        entries = load_entries(zkid)

        for entry, filepath in entries:
            needs_emotion = not bool(entry.get("analysis", {}).get("emotion"))
            needs_context = not bool(entry.get("analysis", {}).get("context"))
            needs_analysis = needs_emotion or needs_context

            if not force and not needs_analysis:
                skipped += 1
                continue

            paragraph_labels = classify_entry(classifiers, entry["text"])

            emotion_frequency = frequency(paragraph_labels, key="emotion")
            context_frequency = frequency(paragraph_labels, key="context")
            sentiment_frequency = frequency(paragraph_labels, key="sentiment")

            # Save labels for each paragraph and their scores
            stats = {
                "frequency": {
                    "emotion": emotion_frequency,
                    "context": context_frequency,
                },
            }
            top_labels = {
                "paragraphs": paragraph_labels,
                "emotion": get_top_labels(emotion_frequency, k=1),
                "context": get_top_labels(context_frequency, k=3),
                "sentiment": get_top_labels(sentiment_frequency, k=1),
            }
            analysis = {"stats": stats, "labels": top_labels}
            # Update entry with emotion tag
            entry["analysis"] = analysis
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
