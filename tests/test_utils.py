from pathlib import Path
from unittest.mock import Mock

import pytest
from appdirs import user_cache_dir, user_config_dir, user_data_dir

from thought_log.utils import common, paths

APP_NAME = "ThoughtLog"
APP_AUTHOR = "SolipsisAI"


@pytest.fixture
def mock_classifier():
    def mock_classify(*args, **kwargs):
        return ["LABEL"]

    _mock = Mock()
    _mock.classify = mock_classify
    yield _mock


@pytest.mark.parametrize("path_fn,expected", [
    (paths.config_path, Path(user_config_dir(APP_NAME, APP_AUTHOR))),
    (paths.cache_path, Path(user_cache_dir(APP_NAME, APP_AUTHOR))),
    (paths.app_data_path, Path(user_data_dir(APP_NAME, APP_AUTHOR))),
])
def test_paths(path_fn, expected):
    assert path_fn() == expected


@pytest.mark.parametrize("with_classifier,text,expected", [
    (True, "hello world", "LABEL hello world"),
    (False, "hello world", "hello world"),
])
def test_preprocess_text(mock_classifier, with_classifier, text, expected):
    classifier = mock_classifier if with_classifier else None
    assert common.preprocess_text(text, classifier=classifier) == expected
