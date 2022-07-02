from pathlib import Path
from unittest.mock import mock_open, patch

import frontmatter

from thought_log.importer import filesystem


def read_data(name):
    filepath = Path(__file__).parent.parent.joinpath("fixtures", name)
    with open(filepath) as f:
        return f.read()


@patch("builtins.open", mock_open(read_data=read_data("entry.md")), create=True)
def test_import_from_file():
    post = filesystem.read_file("test.txt")
    expected_post = frontmatter.loads(read_data("entry.md"))
    assert post.content == expected_post.content


def test_import_from_directory():
    pass
