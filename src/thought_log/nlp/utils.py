from typing import Union

import en_core_web_sm
from spacy.tokens import Doc

DEVICES_MAPPING = {"cuda": 0, "cpu": -1}


def tokenize(text: str) -> Doc:
    nlp = en_core_web_sm.load()
    return nlp(text)


def split_paragraphs(document: Union[Doc, str]):
    if isinstance(document, str):
        document = tokenize(document)

    # https://gist.github.com/wpm/bf1f2301b98a883b50e903bc3cc86439
    start = 0
    for token in document:
        if token.is_space and token.text.count("\n") > 1:
            yield document[start : token.i].text
            start = token.i
    yield document[start:].text


def split_chunks(tokenizer, text: str, per_chunk: int = 512):
    # This fails because we haven't yet split the text into chunks
    doc = tokenize(text)
    num_tokens = len(doc)
    n = per_chunk - len(tokenizer.special_tokens_map)

    if num_tokens <= n:
        yield doc.text

    for i in range(0, num_tokens, n):
        yield doc[i : i + n].text


def get_device(name: str = None) -> int:
    import torch

    try:
        cuda_available = torch.cuda.is_available()

        if name is None:
            return 0 if cuda_available else -1
    except AssertionError:
        return -1
    else:
        return DEVICES_MAPPING.get(name, -1)
