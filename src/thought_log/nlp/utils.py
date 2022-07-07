from typing import Union

import en_core_web_sm
from spacy.tokens import Doc


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
            yield document[start : token.i]
            start = token.i
    yield document[start:]


def split_chunks(text: str, per_chunk: int = 512, num_special: int = 7):
    tokens = tokenize(text)
    num_tokens = len(tokens)
    n = per_chunk - (num_special * num_special)  # leave spaces to add special tokens

    if num_tokens <= n:
        yield [tokens.text]

    for i in range(0, num_tokens, n):
        yield tokens[i : i + n].text
