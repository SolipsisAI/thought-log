import frontmatter

from pathlib import Path
from typing import Union

from thought_log.utils import read_file


def import_from_file(filename: Union[str, Path]):
    """Import from plaintext or markdown"""
    read_file(filename)


def import_from_directory():
    pass
