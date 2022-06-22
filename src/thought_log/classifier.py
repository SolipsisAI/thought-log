from typing import Dict, List, Union

from transformers import PreTrainedModel, PreTrainedTokenizer, pipeline

from thought_log.res import labels


class Classifier:
    def __init__(
        self,
        model: Union[str, PreTrainedModel],
        tokenizer: Union[str, PreTrainedTokenizer],
    ) -> None:
        self.pipe = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            return_all_scores=True,
        )
        self.pipe.model.config.id2label = labels.ID2LABEL
        self.pipe.model.config.label2id = labels.LABEL2ID

    def classify(
        self, text, k: int = 1, include_score=False
    ) -> Union[List[Dict], List[str]]:
        results = self.pipe(text)
        result = results[0] if results else None

        if not result:
            return

        result.sort(key=lambda item: item.get("score"), reverse=True)

        # Return all the results
        if k < 1:
            return result

        # Sort by score, in descending order
        result.sort(key=lambda item: item.get("score"), reverse=True)

        # Return the top k results
        return [r if include_score else r["label"] for r in result[:k]]
