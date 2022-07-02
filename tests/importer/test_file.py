import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import frontmatter

from thought_log.importer import filesystem
from thought_log.utils import make_datetime


def read_data(name):
    filepath = Path(__file__).parent.parent.joinpath("fixtures", name)
    with open(filepath) as f:
        return f.read()


def test_prepare_data_from_frontmatter_post():
    data = frontmatter.loads(read_data("entry.md"))
    assert filesystem.prepare_data(data) == {
        "id": 20220702124938,
        "metadata": {"date": datetime.datetime(2022, 7, 2, 12, 49, 38, 119625)},
        "text": "Hello, world.",
    }


def test_prepare_data_from_dict():
    data = {
        "date": "2018-06-24T22:32:17.676Z",
        "text": "Hello, world.",
        "weatherCode": "mostly-cloudy",
        "country": "United States",
    }
    assert filesystem.prepare_data(data) == {
        "id": 20180624223217,
        "metadata": {"date": datetime.datetime(2018, 6, 24, 22, 32, 17, 676000)},
        "text": "Hello, world.",
        "metadata": data,
    }


@patch("builtins.open", mock_open(read_data=read_data("entry.md")), create=True)
def test_import_from_file():
    post = filesystem.read_file("test.txt")
    expected_post = frontmatter.loads(read_data("entry.md"))
    assert post.content == expected_post.content


def test_import_from_directory():
    pass
