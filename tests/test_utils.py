from pathlib import Path
from unittest.mock import Mock
from datetime import datetime, date, time

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


@pytest.mark.parametrize("text,expected", [
    ("LABEL hello world", "hello world"),
    ("LABEL hello_comma_ world", "hello, world"),
])
def test_postprocess_text(text, expected):
    assert common.postprocess_text(text) == expected


def test_zettelkasten_id():
    datetime_obj = datetime(1989, 10, 1, 12, 0, 0)
    assert common.zettelkasten_id(datetime_obj) == "19891001120000"


def test_find_date():
    assert common.find_date("2022-10-01") == date(2022, 10, 1)


def test_find_time():
    assert common.find_time("15:30:01") == time(15, 30, 1)