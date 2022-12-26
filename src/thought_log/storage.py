from typing import List, Dict, Union

from pymongo import MongoClient, ASCENDING, DESCENDING

from thought_log.config import MONGO_URL, MONGO_DB_NAME


DictList = List[Dict]
StorageObj = Union[Dict, DictList]


ORDER = {
    "ASC": ASCENDING,
    "DESC": DESCENDING,
}


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
        self,
        collection_name: str,
        obj: StorageObj,
        identifier_keys: str = None,
    ):
        find_obj = obj

        if identifier_keys:
            find_obj = dict(map(lambda i: (i, obj.get(i)), identifier_keys))

        self.db[collection_name].replace_one(find_obj, obj, upsert=True)

    def upsert_many(
        self,
        collection_name: str,
        obj: DictList,
        identifier_key: str = None,
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
