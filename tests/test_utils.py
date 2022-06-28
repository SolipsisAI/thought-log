from pathlib import Path

import pytest
from appdirs import user_cache_dir, user_config_dir, user_data_dir

from thought_log.utils import paths

APP_NAME = "ThoughtLog"
APP_AUTHOR = "SolipsisAI"


@pytest.mark.parametrize("path_fn,expected", [
    (paths.config_path, Path(user_config_dir(APP_NAME, APP_AUTHOR))),
    (paths.cache_path, Path(user_cache_dir(APP_NAME, APP_AUTHOR))),
    (paths.app_data_path, Path(user_data_dir(APP_NAME, APP_AUTHOR))),
])
def test_paths(path_fn, expected):
    assert path_fn() == expected
