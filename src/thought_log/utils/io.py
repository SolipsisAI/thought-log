import csv
import json
import datetime
from json import JSONEncoder
from mimetypes import guess_type
from typing import Dict, List

import frontmatter


class DateTimeEncoder(JSONEncoder):
    # https://pynative.com/python-serialize-datetime-into-json/
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


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
        return frontmatter.load(f)
