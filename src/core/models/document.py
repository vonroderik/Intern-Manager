from typing import Optional
from dataclasses import dataclass


@dataclass
class Document:
    """
    Domain model representing a document associated with an intern.

    Each Document represents a required or optional document linked to
    a specific Intern. An intern may have multiple associated documents.

    This class mirrors the structure of the `documents` table in the database.

    Attributes:
        document_id (Optional[int]): Unique database identifier. None if the
            document has not yet been persisted.
        intern_id (int): Identifier of the intern to whom this document belongs.
        document_name (str): Name or description of the document.
        is_completed (int): Completion status of the document.
            Typically uses 0 (not completed) or 1 (completed).
    """

    intern_id: int
    document_name: str
    is_completed: bool
    last_update: Optional[str] = None
    document_id: Optional[int] = None
