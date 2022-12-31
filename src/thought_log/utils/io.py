import csv
import datetime
import hashlib
import json
import zipfile
import tempfile
from io import TextIOWrapper
from json import JSONEncoder
from mimetypes import guess_type
from pathlib import Path
from typing import Dict, List, Union
from uuid import uuid4

import frontmatter
from thought_log.enums import SupportedFiletypes


class DateTimeEncoder(JSONEncoder):
    # https://pynative.com/python-serialize-datetime-into-json/
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def generate_hash_from_file(filename: str) -> str:
    """Generate hash based on string or filename"""
    if Path(filename).exists():
        with open(filename, "r") as f:
            content = f.read()
            return generate_hash_from_string(content)


def generate_hash_from_string(text: str) -> str:
    if text is None:
        text = ""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def generate_uuid(dashes: bool = False, uppercase: bool = True) -> str:
    uuid_string = str(uuid4())
    if not dashes:
        uuid_string = uuid_string.replace("-", "")
    if uppercase:
        uuid_string = uuid_string.upper()
    return uuid_string


def get_filetype(filename: str) -> str:
    filetype, _ = guess_type(filename)
    return filetype


def read_csv(fp: Union[str, TextIOWrapper, Path]) -> List[Dict]:
    if isinstance(fp, str) or isinstance(fp, Path):
        fp = open(fp)

    csv_data = csv.DictReader(fp)
    data = list(csv_data)

    fp.close()
    return data


def read_json(fp: Union[str, TextIOWrapper, Path], as_type=None) -> Dict:
    if isinstance(fp, str) or isinstance(fp, Path):
        fp = open(fp, "r")

    data = json.load(fp)

    if as_type is not None:
        data = dict([(as_type(k), v) for k, v in data.items()])

    fp.close()
    return data


def read_zipfile(fp):
    data = []

    zf = zipfile.ZipFile(fp)

    supported_filetypes = [
        SupportedFiletypes.MARKDOWN.value,
        SupportedFiletypes.PLAIN.value,
    ]

    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        dirpath = Path(tempdir)
        filenames = list(
            filter(
                lambda p: not p.is_dir() and get_filetype(p) in supported_filetypes,
                dirpath.glob("**/*"),
            )
        )
        data = list(map(read_file, filenames))

    return data


def write_json(data: Dict, filename: str, mode: str = "w+"):
    with open(filename, mode) as f:
        json.dump(data, f, indent=4, cls=DateTimeEncoder)
        return data


def read_file(fp: Union[str, TextIOWrapper, Path]):
    if isinstance(fp, str) or isinstance(fp, Path):
        fp = open(fp, "r")

    data = frontmatter.load(fp)

    fp.close()
    return data


def sanitize_json_string(json_obj):
    # https://stackoverflow.com/a/64045192
    s = json.dumps(json_obj)
    s = s.replace("\\", "")
    return json.loads(s)
