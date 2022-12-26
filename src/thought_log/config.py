import os
from pathlib import Path

from dotenv import load_dotenv

from thought_log.utils import load_config

load_dotenv()
config = load_config()

DEBUG = os.getenv("DEBUG", False)

# Environment variables take precedence to allow for runtime overrides
STORAGE_DIR_NAME = os.getenv("TL_STORAGE_DIR") or config.get("storage_dir", None)
STORAGE_DIR = Path(STORAGE_DIR_NAME) if STORAGE_DIR_NAME else None

CLASSIFIER_NAME = os.getenv("TL_CLASSIFIER_NAME") or config.get("classifier_path")
SENTIMENT_CLASSIFIER_NAME = os.getenv("TL_SENTIMENT_CLASSIFIER_NAME") or config.get(
    "sentiment_classifier_path"
)
EMOTION_CLASSIFIER_NAME = os.getenv("TL_EMOTION_CLASSIFIER_NAME") or config.get(
    "emotion_classifier_path"
)
MODEL_NAME = os.getenv("TL_MODEL_NAME") or config.get("core_path")
CLASSIFIER_NAMES = {
    "emotion": EMOTION_CLASSIFIER_NAME,
    "sentiment": SENTIMENT_CLASSIFIER_NAME,
    "context": CLASSIFIER_NAME,
}

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or config.get(
    "openweather_api_key"
)
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION") or config.get(
    "default_location"
)  # example: "New York, US"
INCLUDE_WEATHER = bool(
    os.getenv("INCLUDE_WEATHER") or config.get("include_weather", False)
)

# MongoDB
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "chat_history")
MONGO_ROOT_USERNAME = os.getenv("MONGO_ROOT_USERNAME")
MONGO_ROOT_PASSWORD = os.getenv("MONGO_ROOT_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_CONNECTION_STRING = f"mongodb://{MONGO_ROOT_USERNAME}:{MONGO_ROOT_PASSWORD}@{MONGO_HOST}/{MONGO_DB_NAME}?authSource=admin"
MONGO_URL = os.getenv("MONGO_URL", MONGO_CONNECTION_STRING)
