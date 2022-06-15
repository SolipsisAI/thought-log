from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent.resolve()
DATA_DIR = ROOT_DIR.joinpath("data")
ID2LABEL_FILEPATH = DATA_DIR.joinpath("id2label.json")
LABEL2ID_FILEPATH = DATA_DIR.joinpath("label2id.json")
