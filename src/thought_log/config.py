from pathlib import Path

from thought_log.utils import read_config

config = read_config()

STORAGE_DIR = Path(config.get("storage_dir"))
CLASSIFIER_NAME = config.get("classifier_path")
MODEL_NAME = config.get("core_path")
