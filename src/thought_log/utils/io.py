import csv
import datetime
import hashlib
import json
from json import JSONEncoder
from mimetypes import guess_type
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

import frontmatter


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


def read_csv(filename: str) -> List[Dict]:
    with open(filename) as f:
        csv_data = csv.DictReader(f)
        return list(csv_data)


def read_json(filename: str, as_type=None) -> Dict:
    with open(filename, "r") as json_file:
        data = json.load(json_file)

        if as_type is not None:
            data = dict([(as_type(k), v) for k, v in data.items()])

        return data


def write_json(data: Dict, filename: str, mode: str = "w+"):
    with open(filename, mode) as f:
        json.dump(data, f, indent=4, cls=DateTimeEncoder)
        return data


def read_file(filename: str):
    with open(filename, "r") as f:
        data = frontmatter.load(f)
        return data


def sanitize_json_string(json_obj):
    # https://stackoverflow.com/a/64045192
    s = json.dumps(json_obj)
    s = s.replace("\\", "")
    return json.loads(s)
