import json
import re
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent.resolve()
DATA_DIR = ROOT_DIR.joinpath("data")
ID2LABEL_FILEPATH = DATA_DIR.joinpath("id2label.json")
LABEL2ID_FILEPATH = DATA_DIR.joinpath("label2id.json")


def read_json(filename: str, as_type=None) -> Dict:
    with open(filename, "r") as json_file:
        data = json.load(json_file)

        if as_type is not None:
            data = dict([(as_type(k), v) for k, v in data.items()])

        return data


def preprocess_text(text, classifier=None):
    """Prepend context label if classifier specified"""
    prefix = ""
    if classifier:
        context_label = classifier.classify(text, k=1)[0]
        prefix = f"{context_label} "
    return f"{prefix}{text}"


def postprocess_text(text):
    """Clean response text"""
    text = re.sub(r"^\w+\s", "", text)
    return re.sub(r"_comma_", ",", text)
