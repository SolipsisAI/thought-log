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
        )
        # TODO: Move these to the model files
        self.pipe.model.config.id2label = labels.ID2LABEL
        self.pipe.model.config.label2id = labels.LABEL2ID
        # This is deprecated, but the recommended param top_k=1 is not working
        self.pipe.model.config.return_all_scores = True

    def classify(
        self, text, k: int = 1, include_score=False
    ) -> Union[List[Dict], List[str]]:
        results = self.pipe(text)

        if not results:
            return

        if k is None:
            return results

        # Sort by score, in descending order
        results.sort(key=lambda item: item.get("score"), reverse=True)

        # Return the top k results
        return [r if include_score else r["label"] for r in results[:k]]
