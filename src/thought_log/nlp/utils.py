from pydoc import doc
from typing import Union

import en_core_web_sm
from spacy.tokens import Doc


def paragraphs(document: Union[Doc, str]):
    if isinstance(document, str):
        nlp = en_core_web_sm.load()
        document = nlp(document)

    # https://gist.github.com/wpm/bf1f2301b98a883b50e903bc3cc86439
    start = 0
    for token in document:
        if token.is_space and token.text.count("\n") > 1:
            yield document[start : token.i]
            start = token.i
    yield document[start:]
