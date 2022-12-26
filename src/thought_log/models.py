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
        "timestamp",
        "edited_timestamp",
    ]

    def __init__(
        self, data, base_fields: List[str], add_fields: List[str] = None
    ) -> None:
        super().__init__(data, base_fields, add_fields)
