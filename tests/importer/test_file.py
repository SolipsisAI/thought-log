from unittest.mock import mock_open, patch

import pytest
import frontmatter

from thought_log.importer import filesystem


@patch("builtins.open", mock_open(read_data="test"), create=True)
def test_import_from_file():
    post = filesystem.read_file("test.txt")
    expected_post = frontmatter.loads("test")
    assert post.content == expected_post.content


def test_import_from_directory():
    pass
