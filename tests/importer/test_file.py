import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import frontmatter

from thought_log.importer import filesystem


def read_data(name):
    filepath = Path(__file__).parent.parent.joinpath("fixtures", name)
    with open(filepath) as f:
        return f.read()


def test_prepare_data_from_frontmatter_post():
    data = frontmatter.loads(read_data("entry.md"))
    date = datetime.datetime(2022, 7, 2, 12, 49, 38, 119625)
    result = filesystem.prepare_data(data, "fakehash")
    result.pop("uuid")
    assert result == {
        "id": 20220702124938,
        "_hash": "fakehash",
        "metadata": {"date": date},
        "date": date,
        "text": "Hello, world.",
    }


def test_prepare_data_from_dict():
    data = {
        "date": "2018-06-24T22:32:17.676Z",
        "text": "Hello, world.",
        "weatherCode": "mostly-cloudy",
        "country": "United States",
    }
    date = datetime.datetime(2018, 6, 24, 22, 32, 17)
    result = filesystem.prepare_data(data, "fakehash")
    result.pop("uuid")
    assert result == {
        "id": 20180624223217,
        "_hash": "fakehash",
        "metadata": data,
        "date": date,
        "text": "Hello, world.",
    }


def test_prepare_data_from_string():
    data = read_data("entry.txt")
    date = datetime.datetime(1969, 1, 1)
    result = filesystem.prepare_data(data, "fakehash")
    result.pop("uuid")
    assert result == {
        "id": 19690101000000,
        "_hash": "fakehash",
        "metadata": {},
        "date": date,
        "text": "DATE: 1969-01-01\n\nHello, world.",
    }


@patch("builtins.open", mock_open(read_data=read_data("entry.md")), create=True)
def test_import_from_file():
    post = filesystem.read_file("test.txt")
    expected_post = frontmatter.loads(read_data("entry.md"))
    assert post.content == expected_post.content


def test_import_from_directory():
    pass
