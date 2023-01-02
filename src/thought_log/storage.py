import json
from typing import List, Dict, Union

from pymongo import MongoClient, ASCENDING, DESCENDING

from thought_log.config import MONGO_URL, MONGO_DB_NAME
from thought_log.utils import timestamp, make_datetime
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
    BASE_FIELDS = ["id", "uuid", "created", "edited"]

    def __init__(
        self, data, base_fields: List[str], add_fields: List[str] = None
    ) -> None:
        self._data = self.sanitize(data)
        self._fields = self.BASE_FIELDS + base_fields + (add_fields or [])

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
        identifiers = {}

        if bool(self.hash):
            identifiers["hash"] = self.hash
        else:
            if bool(self.id):
                identifiers["id"] = self.id
            if bool(self.uuid):
                identifiers["uuid"] = self.uuid

        existing = self.get(**identifiers)

        if not existing:
            return self.insert(self)

        return self.update(self.data, **identifiers)

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

    def get_children(
        self, limit: int = None, order_by: str = None, sort_by: str = None
    ):
        if not self.HAS_MANY:
            return None

        return storage.query(
            self.HAS_MANY.COLLECTION_NAME,
            {self.FOREIGN_FIELD: self.id},
            sort=sort_by,
            order=order_by,
            limit=limit,
            callback=self.HAS_MANY,
        )

    @classmethod
    def convert(cls, o):
        if not isinstance(o, cls):
            o = cls(o)
        return o.to_dict()

    @classmethod
    def insert(cls, obj):
        obj = cls.convert(obj)

        result = storage.insert(
            cls.COLLECTION_NAME,
            obj,
        )

        return cls.get(_id=result.inserted_id)

    @classmethod
    def update(cls, obj, **filter):
        obj.update(filter)

        result = storage.update(
            cls.COLLECTION_NAME,
            obj,
            filter=filter,
        )

        return cls.get(**filter)

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
        self._data = self.sanitize(updatedData)

    @property
    def fields(self):
        return self._fields

    def from_dict(self, data: Dict):
        if not isinstance(data, Dict):
            return

        for field in self.fields:
            value = data.get(field, None)
            setattr(self, field, value)

    def to_json(
        self,
        embed: str = None,
        limit: int = None,
        order_by: str = None,
        sort_by: str = None,
    ):
        return json.dumps(
            self.to_dict(embed=embed, limit=limit, order_by=order_by, sort_by=sort_by)
        )

    def to_dict(
        self,
        embed: str = None,
        limit: int = None,
        order_by: str = None,
        sort_by: str = None,
    ):
        def filter_data(item):
            return not item[0].startswith(IGNORE_PREFIX)

        result = dict(list(filter(filter_data, self.__dict__.items())))

        if embed:
            children = getattr(self, embed)(
                limit=limit, order_by=order_by, sort_by=sort_by
            )
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

    def insert(self, collection_name: str, obj: StorageObj):
        obj["id"] = self.get_next_sequence(collection_name, "id")

        created = obj.pop("created", None)
        uuid = obj.pop("uuid", None)
        obj["created"] = timestamp(created)
        obj["uuid"] = uuid or generate_uuid()
        return self.db[collection_name].insert_one(obj)

    def update(self, collection_name: str, obj: StorageObj, filter: Dict):
        edited = obj.pop("edited", None)
        obj["edited"] = timestamp(edited)
        return self.db[collection_name].update_one(filter, {"$set": obj})

    def get_next_sequence(self, collection_name, autoincrement):
        last_obj = self.last(collection_name) or {}
        sequence_value = last_obj.get(autoincrement, 1)

        if last_obj:
            sequence_value += 1

        return sequence_value

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
