import json
from typing import List, Dict, Union

from pymongo import MongoClient, ASCENDING, DESCENDING

from thought_log.config import MONGO_URL, MONGO_DB_NAME
from thought_log.utils import timestamp
from thought_log.utils.io import generate_uuid


DictList = List[Dict]
StorageObj = Union[Dict, DictList]


ORDER = {
    "ASC": ASCENDING,
    "DESC": DESCENDING,
}
IGNORE_PREFIX = "_"


class BaseDocument:
    COLLECTION_NAME = None
    HAS_MANY = None
    BELONGS_TO = None
    FOREIGN_FIELD = None

    def __init__(
        self, data, base_fields: List[str], add_fields: List[str] = None
    ) -> None:
        self._data = self.sanitize(data)
        self._fields = base_fields + (add_fields or [])
        self._created = None
        self._edited = None
        self.uuid = data.get("uuid") or generate_uuid()

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

    def save(self):
        self.upsert(self)

    @classmethod
    def get(cls, **kwargs):
        return cls.find_one(kwargs)

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
        result = storage.db[cls.COLLECTION_NAME].find_one(*args, **kwargs)
        return cls(result) if result else None

    # setattr
    def _get_children(self):
        cursor = storage.db[self.COLLECTION_NAME].aggregate(
            [
                {"$match": {"id": self.id}},
                {
                    "$lookup": {
                        "from": self.HAS_MANY.COLLECTION_NAME,
                        "localField": f"id",
                        "foreignField": f"{self.COLLECTION_NAME[:-1]}",
                        "as": "joinedResult",
                    }
                },
                {
                    "$unwind": {
                        "path": "$joinedResult",
                        "preserveNullAndEmptyArrays": True,
                    }
                },
                {"$sort": {"joinedResult.created": -1}},
            ]
        )

        results = list(map(lambda r: r["joinedResult"], cursor))

        if not results:
            return []

        return list(map(self.HAS_MANY, results))

    def get_children(self, limit: int = None):
        if not self.HAS_MANY:
            return None

        return storage.query(
            self.HAS_MANY.COLLECTION_NAME,
            {self.FOREIGN_FIELD: self.id},
            sort="created",
            order="DESC",
            limit=limit,
            callback=self.HAS_MANY,
        )

    @classmethod
    def upsert(cls, obj):
        def convert(o):
            if not isinstance(o, cls):
                o = cls(o)
            return o.to_dict()

        if isinstance(obj, List):
            obj = list(map(convert, obj))
        else:
            obj = convert(obj)

        storage.upsert(
            cls.COLLECTION_NAME,
            obj,
            identifier_keys=cls.IDENTIFIER_KEYS,
            autoincrement=cls.AUTOINCREMENT,
        )

    @classmethod
    def last(cls):
        """Return the last object"""
        results = storage.query(
            cls.COLLECTION_NAME, sort="$natural", order="DESC", limit=1
        )
        return cls(results[0]) if results else None

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

        for field in self.fields:
            value = data.get(field, None)
            setattr(self, field, value)

    def to_json(self, embed: str = None):
        return json.dumps(self.to_dict(embed=embed))

    def to_dict(self, embed: str = None):
        def filter_data(item):
            return not item[0].startswith(IGNORE_PREFIX)

        result = dict(list(filter(filter_data, self.__dict__.items())))

        if embed:
            children = getattr(self, embed)()
            result[embed] = list(map(lambda c: c.to_dict(), children))

        return result


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
        self,
        collection_name: str,
        obj: StorageObj,
        find_obj: StorageObj = None,
        identifier_keys: List[str] = None,
        autoincrement: str = None,
    ):
        if not obj:
            return

        if isinstance(obj, Dict):
            self.upsert_one(
                collection_name,
                obj,
                find_obj=find_obj,
                identifier_keys=identifier_keys,
                autoincrement=autoincrement,
            )
        elif isinstance(obj, List):
            self.upsert_many(
                collection_name,
                obj,
                find_obj=find_obj,
                identifier_keys=identifier_keys,
                autoincrement=autoincrement,
            )

    def upsert_one(
        self,
        collection_name: str,
        obj: StorageObj,
        find_obj: StorageObj = None,
        identifier_keys: str = None,
        autoincrement: str = None,
    ):
        if not find_obj:
            find_obj = obj

        has_autoincrement = bool(autoincrement) and autoincrement not in obj

        has_id = bool(obj.get("id", None))
        has_uuid = bool(obj.get("uuid", None))
        has_file_hash = bool(obj.get("file_hash", None))
        has_identifiers = any([has_id, has_uuid, has_file_hash])

        is_new_obj = has_autoincrement or not has_identifiers

        if is_new_obj:
            # Only get next sequence if storage obj doesn't have the autoincremented value
            find_obj.update(
                {
                    autoincrement: self.get_next_sequence(
                        collection_name, autoincrement
                    ),
                }
            )
            obj.update({"created": obj.get("created", timestamp())})
        else:
            if has_id:
                find_obj = {"id": obj["id"]}
            elif has_file_hash and not has_id:
                find_obj = {"file_hash": obj["file_hash"]}
            elif has_uuid:
                find_obj = {"uuid": obj["uuid"]}
            elif identifier_keys:
                find_obj = dict(map(lambda i: (i, obj.get(i)), identifier_keys))

            # Check if the item actually exists
            old_obj = self.db[collection_name].find_one(find_obj)
            if old_obj:
                # So that we don't erase this
                obj.pop("id")
                old_obj.update(obj)
                obj = old_obj
                obj.update({"edited": obj.get("edited", timestamp())})
            else:
                obj.update(
                    {
                        "id": self.get_next_sequence(collection_name, autoincrement),
                    },
                )

        self.db[collection_name].replace_one(find_obj, obj, upsert=True)

    def get_next_sequence(self, collection_name, autoincrement):
        last_obj = self.last(collection_name) or {}
        sequence_value = last_obj.get(autoincrement, 1)

        if last_obj:
            sequence_value += 1

        return sequence_value

    def upsert_many(
        self,
        collection_name: str,
        obj: DictList,
        find_obj: StorageObj = None,
        identifier_keys: List[str] = None,
        autoincrement: str = None,
    ):
        for item in obj:
            self.upsert_one(
                collection_name,
                item,
                find_obj=find_obj,
                identifier_keys=identifier_keys,
                autoincrement=autoincrement,
            )

    def last(self, collection_name: str):
        results = storage.query(
            collection_name=collection_name, sort="$natural", order="DESC", limit=1
        )
        return results[0] if results else None

    def query(
        self,
        collection_name: str,
        params: Dict = None,
        sort: str = None,
        order: str = "asc",
        limit: int = None,
        callback=None,
    ):
        def prepare(item):
            return callback(item) if callback else item

        items = self.db[collection_name].find(params)

        if sort:
            items = items.sort(sort, ORDER.get(order.upper(), ASCENDING))

        if limit:
            items = items.limit(limit)

        return [prepare(item) for item in items]


storage = Storage()
