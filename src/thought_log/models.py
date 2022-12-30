from typing import List
from thought_log.storage import BaseDocument


class Note(BaseDocument):
    COLLECTION_NAME = "notes"
    FIELDNAMES = [
        "id",
        "uuid",
        "title",
        "text",
        "notebook",
        "created",
        "edited",
    ]
    AUTOINCREMENT = "id"
    IDENTIFIER_KEYS = ["id"]
    BELONGS_TO = "notebook"

    def __init__(self, data, add_fields: List[str] = None):
        super().__init__(data=data, base_fields=self.FIELDNAMES, add_fields=add_fields)
        self.from_dict(self.data)


class Notebook(BaseDocument):
    COLLECTION_NAME = "notebooks"
    FIELDNAMES = [
        "id",
        "uuid",
        "title",
        "description",
        "created",
        "edited",
    ]
    AUTOINCREMENT = "id"
    IDENTIFIER_KEYS = ["id"]
    HAS_MANY = "notes"

    def __init__(self, data, add_fields: List[str] = None):
        super().__init__(data=data, base_fields=self.FIELDNAMES, add_fields=add_fields)
        self.from_dict(self.data)

    def notes(self):
        results = list(self.get_children())

        if not results:
            return []

        return results[0]["joinedResult"]


MODELS = {"notes": Note, "notebooks": Notebook}
