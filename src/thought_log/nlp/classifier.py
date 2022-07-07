from typing import Dict, List, Union

import pandas as pd
from transformers import PreTrainedModel, PreTrainedTokenizer, pipeline

from thought_log.config import CLASSIFIER_NAME
from thought_log.utils import flatten
from thought_log.nlp.utils import split_chunks


class Classifier:
    def __init__(
        self,
        model: Union[str, PreTrainedModel] = CLASSIFIER_NAME,
        tokenizer: Union[str, PreTrainedTokenizer] = CLASSIFIER_NAME,
        device: str = "cpu",
    ) -> None:
        self.pipe = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            device=0 if device == "cuda" else -1,
        )
        # This is deprecated, but the recommended param top_k=1 is not working
        self.pipe.model.config.return_all_scores = True
        self.max_length = self.pipe.model.config.max_length
        self.max_position_embeddings = self.pipe.model.config.max_position_embeddings
        # For reference
        self.label2id = self.pipe.model.config.label2id
        self.id2label = self.pipe.model.config.id2label
        # Resize embeddings
        self.pipe.model.resize_token_embeddings(len(self.pipe.tokenizer))

    def classify(
        self, text, k: int = 1, include_score: bool = False, only_mean: bool = False
    ):
        results = self.__call__(text=text, k=k)
        df = pd.DataFrame.from_records(results)
        mean = df.groupby("label").mean()
        if only_mean:
            return mean

        label = mean.score.idxmax()
        score = mean.score.max()

        return {"label": label, "score": score} if include_score else label

    def __call__(self, text, *, k: int = 1) -> Union[List[Dict], List[str]]:
        chunks = list(
            split_chunks(
                tokenizer=self.pipe.tokenizer,
                text=text,
                per_chunk=self.max_position_embeddings,
            )
        )
        results = self.pipe(chunks, top_k=k)
        return flatten(results)
