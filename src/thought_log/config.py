import os
from pathlib import Path

from thought_log.utils import load_config

config = load_config()

STORAGE_DIR_NAME = os.getenv("TL_STORAGE_DIR") or config.get("storage_dir", None)
STORAGE_DIR = Path(STORAGE_DIR_NAME) if STORAGE_DIR_NAME else None
CLASSIFIER_NAME = os.getenv("TL_CLASSIFIER_NAME") or config.get("classifier_path")
MODEL_NAME = os.getenv("TL_MODEL_NAME") or config.get("core_path")
