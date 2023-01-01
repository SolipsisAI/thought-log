from typing import List
from thought_log.storage import BaseDocument
from thought_log.utils import generate_hash_from_string, datestring


class Note(BaseDocument):
    COLLECTION_NAME = "notes"
    FIELDNAMES = [
        "title",  # Cannot be null
        "text",
        "notebook",
        "created",
        "edited",
        "file_hash",
    ]

    def __init__(self, data, add_fields: List[str] = None):
        super().__init__(data=data, base_fields=self.FIELDNAMES, add_fields=add_fields)
        self.from_dict(self.data)
        # Overrides
        self.file_hash = generate_hash_from_string(self.text)


class Notebook(BaseDocument):
    COLLECTION_NAME = "notebooks"
    FIELDNAMES = [
        "title",
        "description",
        "created",
        "edited",
    ]
    HAS_MANY = Note
    FOREIGN_FIELD = "notebook"

    def __init__(self, data, add_fields: List[str] = None):
        super().__init__(data=data, base_fields=self.FIELDNAMES, add_fields=add_fields)
        self.from_dict(self.data)

    def notes(self, limit: int = None):
        return self.get_children(limit=limit)


MODELS = {"notes": Note, "notebooks": Notebook}
