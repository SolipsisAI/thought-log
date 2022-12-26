import json
from typing import List, Dict, Union

from pymongo import MongoClient, ASCENDING, DESCENDING

from thought_log.config import MONGO_URL, MONGO_DB_NAME


DictList = List[Dict]
StorageObj = Union[Dict, DictList]


ORDER = {
    "ASC": ASCENDING,
    "DESC": DESCENDING,
}
IGNORE_PREFIX = "_"


class BaseDocument:
    def __init__(
        self, data, base_fields: List[str], add_fields: List[str] = None
    ) -> None:
        self._data = self.sanitize(data)
        self._fields = base_fields + (add_fields or [])

    def sanitize(self, data):
        if isinstance(data, Dict):
            # Typecast to string so GraphQL can support it
            for k, v in data.items():
                if "_id" in k and isinstance(v, int):
                    data[k] = str(v)
        else:
            for k in dir(data):
                if "_id" in k:
                    v = getattr(data, k)
                    setattr(data, k, str(v))
        return data

    @classmethod
    def find(cls, *args, **kwargs):
        """Returns a list of results"""
        return list(map(cls, cls.find_cursor(*args, **kwargs)))

    @classmethod
    def find_cursor(cls, *args, **kwargs):
        """Returns a cursor"""
        return storage.db[cls.COLLECTION_NAME].find(*args, **kwargs)

    @classmethod
    def find_one(cls, *args, **kwargs):
        """Returns an instance of the class"""
        return cls(storage.db[cls.COLLECTION_NAME].find_one(*args, **kwargs))

    @classmethod
    def upsert(cls, obj, identifier_keys: List[str] = None):
        def convert(o):
            if not isinstance(o, cls):
                o = cls(o)
            return o.to_dict()

        if isinstance(obj, List):
            obj = list(map(convert, obj))
        else:
            obj = convert(obj)

        storage.upsert(cls.COLLECTION_NAME, obj, identifier_keys=identifier_keys)

    @classmethod
    def last(cls):
        """Return the last object"""
        results = storage.query(
            cls.COLLECTION_NAME, sort="$natural", order="DESC", limit=1
        )
        return results[0] if results else None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, updatedData):
        self._data = updatedData

    @property
    def fields(self):
        return self._fields

    def from_dict(self, data: Dict):
        if not isinstance(data, Dict):
            return

        for k, v in data.items():
            if k in self.fields:
                setattr(self, k, v)

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_dict(self):
        return dict(
            list(
                filter(
                    lambda i: not i[0].startswith(IGNORE_PREFIX), self.__dict__.items()
                )
            )
        )


class Storage:
    def __init__(self, db_name: str = MONGO_DB_NAME):
        self._client = MongoClient(MONGO_URL)
        self._db = self._client[db_name]

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._db

    def upsert(
        self, collection_name: str, obj: StorageObj, identifier_keys: List[str] = None
    ):
        if not obj:
            return

        if isinstance(obj, Dict):
            self.upsert_one(collection_name, obj, identifier_keys)
        elif isinstance(obj, List):
            self.upsert_many(collection_name, obj, identifier_keys)

    def upsert_one(
        self, collection_name: str, obj: StorageObj, identifier_keys: str = None,
    ):
        find_obj = obj

        if identifier_keys:
            find_obj = dict(map(lambda i: (i, obj.get(i)), identifier_keys))

        self.db[collection_name].replace_one(find_obj, obj, upsert=True)

    def upsert_many(
        self, collection_name: str, obj: DictList, identifier_key: str = None,
    ):
        for item in obj:
            self.upsert_one(collection_name, item, identifier_key)

    def query(
        self,
        collection_name: str,
        params: Dict = None,
        sort: str = None,
        order: str = "asc",
        limit: int = None,
    ):
        items = self.db[collection_name].find(params)

        if sort:
            items = items.sort(sort, ORDER.get(order.upper(), ASCENDING))

        if limit:
            items = items.limit(limit)

        return [item for item in items]


storage = Storage()
