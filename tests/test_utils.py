from pathlib import Path
from unittest.mock import Mock

import pytest
from appdirs import user_cache_dir, user_config_dir, user_data_dir

from thought_log.utils import common, paths

APP_NAME = "ThoughtLog"
APP_AUTHOR = "SolipsisAI"


@pytest.mark.parametrize("path_fn,expected", [
    (paths.config_path, Path(user_config_dir(APP_NAME, APP_AUTHOR))),
    (paths.cache_path, Path(user_cache_dir(APP_NAME, APP_AUTHOR))),
    (paths.app_data_path, Path(user_data_dir(APP_NAME, APP_AUTHOR))),
])
def test_paths(path_fn, expected):
    assert path_fn() == expected


def test_preprocess_text_no_classifier():
    assert common.preprocess_text("testing") == "testing"


def test_preprocess_text_with_classifier():
    def mock_classify(text, *args, **kwargs):
        return f"LABEL {text}"
    classifier_mock = Mock()
    classifier_mock.classify = mock_classify
    assert classifier_mock.classify("Test") == "LABEL Test"