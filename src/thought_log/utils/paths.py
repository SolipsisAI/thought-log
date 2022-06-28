from pathlib import Path

from appdirs import user_cache_dir, user_config_dir, user_data_dir

APP_NAME = "ThoughtLog"
APP_AUTHOR = "SolipsisAI"


def config_path():
    return Path(user_config_dir(APP_NAME, APP_AUTHOR))


def cache_path():
    return Path(user_cache_dir(APP_NAME, APP_AUTHOR))


def app_data_path():
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def models_data_path():
    return app_data_path().joinpath("models")


def create_app_dirs():
    paths = [
        config_path(),
        cache_path(),
        app_data_path(),
        models_data_path(),
    ]
    for path in paths:
        if not path.exists():
            # Create user data directory
            path.mkdir(parents=True)
