from typing import Optional


class Document:
    def __init__(
        self,
        intern_id: int,
        document_name: str,
        is_completed: int,
        document_id: Optional[int] = None,
    ):
        self.intern_id = intern_id
        self.document_name = document_name
        self.is_completed = is_completed
        self.document_id = document_id
